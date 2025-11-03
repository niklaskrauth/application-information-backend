from typing import Dict, Any, List, Optional
import logging
from app.config import settings
import json
import time

logger = logging.getLogger(__name__)

# Import Ollama and handle connection errors
try:
    from langchain_ollama import ChatOllama
except ImportError:
    ChatOllama = None
    logger.warning("langchain-ollama is not installed. Install it with: pip install langchain-ollama")

# Build tuple of connection error types to handle
def _get_connection_errors():
    """Get tuple of connection error types based on available libraries"""
    errors = [ConnectionRefusedError, ConnectionError]
    
    try:
        import requests
        errors.append(requests.exceptions.ConnectionError)
    except ImportError:
        pass
    
    try:
        import httpx
        errors.append(httpx.ConnectError)
    except ImportError:
        pass
    
    return tuple(errors)

ConnectionErrors = _get_connection_errors()

# Job types to exclude from results (trainee, internship, student positions, managers)
EXCLUDED_JOB_TYPES = [
    "Auszubildung", "Auszubildende", "Auszubildender", "Azubi",
    "Praktikum", "Praktikant", "Praktikanten", "Praktikantin",
    "Studium", "Student", "Studenten", "Studentin", "Studentische",
    "Abteilungsleiter", "Abteilungsleiterin", "Abteilungsleitung",
    "Manager", "Managerin", "Management",
    "Geschäftsführer", "Geschäftsführerin", "Geschäftsführung",
    "Direktor", "Direktorin", "Direktion",
    "Leiter", "Leiterin", "Leitung"
]

# Administrative job types to include (whitelist)
INCLUDED_JOB_TYPES = [
    "Verwaltung", "Verwaltungsfachangestellte", "Verwaltungsmitarbeiter",
    "Sachbearbeiter", "Sachbearbeiterin", "Sachbearbeitung",
    "Sekretariatskraft", "Sekretariat", "Sekretär", "Sekretärin",
    "Bürokraft", "Bürokaufmann", "Bürokauffrau", "Büromitarbeiter",
    "Verwaltungsangestellte", "Verwaltungsassistent",
    "Büroassistent", "Büroassistenz",
    "Kaufmännisch", "Kaufmann", "Kauffrau",
    "Assistenz", "Assistent"
]

# Qualification terms that indicate positions requiring higher education
EXCLUDED_QUALIFICATIONS = [
    "Bachelor", "Master", "Diplom", "Hochschulabschluss",
    "Universitätsabschluss", "Akademiker", "B.Sc.", "M.Sc.", "B.A.", "M.A.",
    "Fachhochschule", "Universität"
]


class AIAgent:
    """LangChain AI Agent using Ollama for analyzing job information from websites"""
    
    # Configuration constants
    MAX_CHUNK_LENGTH = 12000  # Characters per chunk for processing
    
    def __init__(self):
        self.provider = "ollama"
        self.enabled = False
        self.llm: Optional[Any] = None
        
        if ChatOllama is None:
            logger.error("Ollama provider requires langchain-ollama. Install it with: pip install langchain-ollama")
            return
        
        try:
            self.enabled = True
            self.llm = ChatOllama(
                model=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_BASE_URL,
                temperature=0.1,  # Lower temperature for more consistent results
                num_ctx=4096,  # Reduced context window for efficiency
                timeout=90  # Increased timeout for remote server
            )
            logger.info(f"AI Agent initialized with Ollama provider (model: {settings.OLLAMA_MODEL}, base_url: {settings.OLLAMA_BASE_URL})")
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama: {str(e)}. AI agent will be disabled. Make sure Ollama is running at {settings.OLLAMA_BASE_URL}")
            self.enabled = False
            return
        
        # Initialize to current time to avoid artificial delay on first call
        self.last_api_call_time = time.time()
        self.min_delay_between_calls = 0  # No rate limiting for Ollama
        # Set reasonable content length for chunking
        self.max_chunk_length = self.MAX_CHUNK_LENGTH
    
    def _rate_limit(self):
        """Implement rate limiting by adding delays between API calls"""
        # No rate limiting for Ollama - removed delay
        pass
    
    def _chunk_content(self, content: str, max_length: int = None) -> List[str]:
        """
        Split content into chunks for more efficient processing.
        
        The chunking strategy attempts to split at natural boundaries:
        1. First tries to split at paragraph breaks (\\n\\n)
        2. Falls back to sentence breaks (. ) if no paragraph break found
        3. Only splits at arbitrary positions as a last resort
        
        Args:
            content: The content to chunk
            max_length: Maximum length of each chunk (defaults to self.max_chunk_length)
            
        Returns:
            List of content chunks
        """
        if max_length is None:
            max_length = self.max_chunk_length
        
        # If content is small enough, return as single chunk
        if len(content) <= max_length:
            return [content]
        
        chunks = []
        current_pos = 0
        
        while current_pos < len(content):
            # Get next chunk
            chunk_end = current_pos + max_length
            
            # If not at end, try to break at a paragraph or sentence boundary
            if chunk_end < len(content):
                # Look for paragraph break
                para_break = content.rfind('\n\n', current_pos, chunk_end)
                if para_break > current_pos:
                    chunk_end = para_break
                else:
                    # Look for sentence break
                    sentence_break = content.rfind('. ', current_pos, chunk_end)
                    if sentence_break > current_pos:
                        chunk_end = sentence_break + 1
            
            chunks.append(content[current_pos:chunk_end])
            current_pos = chunk_end
        
        return chunks
    
    def extract_multiple_jobs(self, location: str, website: str, website_to_jobs: str, page_content: str, source_url: str = None) -> List[Dict[str, Any]]:
        """
        Extract ALL job information from website content using AI.
        Returns a list of job dictionaries, one for each job found.
        
        Args:
            location: Location from Excel
            website: Main website URL
            website_to_jobs: Jobs page URL
            page_content: Text content from the jobs page
            source_url: The actual URL where this content was found (for foundOn field)
            
        Returns:
            List of dictionaries with job information (one per job)
        """
        if not self.enabled:
            return [{
                "hasJob": False,
                "comments": "AI analysis disabled - langchain-ollama not installed or Ollama not running"
            }]
        
        # Default source_url to website_to_jobs if not provided
        if source_url is None:
            source_url = website_to_jobs
        
        try:
            # Chunk content for more efficient processing
            chunks = self._chunk_content(page_content)
            all_jobs = []
            
            # Get current date for "ab sofort" conversions
            from datetime import datetime
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Build exclusion and inclusion lists for prompt
            excluded_terms = '", "'.join(EXCLUDED_JOB_TYPES)
            included_terms = '", "'.join(INCLUDED_JOB_TYPES)
            excluded_qualifications = '", "'.join(EXCLUDED_QUALIFICATIONS)
            
            for chunk_idx, chunk in enumerate(chunks):
                logger.info(f"Processing chunk {chunk_idx + 1}/{len(chunks)} for {location}")
                
                prompt = f"""Analysieren Sie den folgenden Text SEHR GRÜNDLICH und extrahieren Sie NUR Verwaltungs- und Bürostellen.

Standort: {location}
Heutiges Datum: {current_date}
Quelle URL: {source_url}

KRITISCHE FILTERREGELN - Extrahieren Sie NUR Stellen wenn ALLE Bedingungen erfüllt sind:
1. Die Stelle ist eine Verwaltungs- oder Büroposition (z.B. "{included_terms}")
2. Die Stelle enthält NICHT diese Begriffe: "{excluded_terms}"
3. Die Stelle erfordert KEINE höhere Ausbildung: "{excluded_qualifications}"
4. Die Stelle ist KEINE Führungsposition (kein Leiter/Manager/Direktor)
5. Die Stelle ist für Personen mit Berufsausbildung geeignet

Text:
{chunk}

Geben Sie ein JSON-Array zurück. Jedes Element repräsentiert EINE gefundene Stelle.
WICHTIG: Seien Sie EXTREM GRÜNDLICH und erfassen Sie ALLE relevanten Informationen!

[
  {{
    "hasJob": true,
    "name": "Exakter vollständiger Stellentitel aus dem Text",
    "salary": "Gehaltsinformation (z.B. 'EG 6', 'EG 9a', 'TVÖD', 'E 9b', etc.)" oder null,
    "homeOfficeOption": true oder false (NIEMALS null für gefundene Stellen! true wenn Homeoffice/Remote/mobiles Arbeiten erwähnt wird, sonst false),
    "period": "Arbeitszeit (z.B. 'Vollzeit', 'Teilzeit', 'Vollzeit/Teilzeit')" oder null,
    "employmentType": "Beschäftigungsart (z.B. 'Unbefristet', 'Befristet', 'Befristet bis TT.MM.JJJJ')" oder null,
    "applicationDate": "JJJJ-MM-TT" oder null (letzter Bewerbungstermin/Bewerbungsfrist),
    "occupyStart": "JJJJ-MM-TT" oder null (Stellenantritt/Eintrittsdatum/Besetzungstermin),
    "foundOn": "URL der Quelle wo die Stelle gefunden wurde",
    "comments": "Zusätzliche relevante Informationen (z.B. Voraussetzungen, besondere Hinweise)" oder null
  }}
]

KRITISCHE HINWEISE zu occupyStart (SEHR WICHTIG - NICHT VERGESSEN!):
- Suchen Sie nach: "ab sofort", "nächstmöglich", "zum", "ab", "Einstellungstermin", "Besetzungstermin", "Stellenantritt"
- "ab sofort" oder "nächstmöglich" = {current_date}
- "zum 01.01.2025" = "2025-01-01"
- "ab 15.03.2025" = "2025-03-15"
- Wenn kein Datum erwähnt wird: null
- IMMER nach diesem Feld suchen - es ist SEHR WICHTIG!

KRITISCHE HINWEISE zu salary:
- Suchen Sie nach: "EG", "E ", "TVÖD", "TVöD", "Entgeltgruppe", "Besoldungsgruppe", "A "
- Beispiele: "EG 6", "EG 9a", "E 9b", "TVÖD E 11", "A 9", "Besoldungsgruppe A 10"
- NICHT nur Zahlen - wir brauchen die Entgeltgruppe!
- Wenn nur "TVÖD" erwähnt: "TVÖD" angeben
- IMMER gründlich nach Gehaltsinformationen suchen!

KRITISCHE HINWEISE zu homeOfficeOption:
- Für gefundene Stellen (hasJob=true): NIEMALS null verwenden!
- true wenn: "Homeoffice", "Home-Office", "mobiles Arbeiten", "Remote", "von zuhause" erwähnt wird
- false wenn: nichts davon erwähnt wird
- Standard ist false wenn nicht erwähnt!

KRITISCHE HINWEISE zu foundOn:
- Verwenden Sie IMMER die Quelle URL: {source_url}
- NIEMALS nur "Main page" oder "PDF: filename" - IMMER die vollständige URL!
- Die Quelle URL ist oben angegeben

STRENGE FILTERREGELN:
- NUR Stellen extrahieren die ALLE Filterkriterien erfüllen
- KEINE Ausbildungs-, Praktikums- oder Studenten-Stellen
- KEINE Führungspositionen (Leiter, Manager, Direktor, etc.)
- KEINE Stellen die Bachelor/Master/Hochschulabschluss erfordern
- Seien Sie EXTREM GRÜNDLICH - vergessen Sie KEINE wichtigen Informationen!
- Lesen Sie den GESAMTEN Text sorgfältig durch!
- Bei Unsicherheit ob Führungsposition: NICHT extrahieren
- Wenn KEINE passende Stelle: [{{"hasJob": false, "comments": "Keine passenden Verwaltungsstellen gefunden"}}]

Antworten Sie NUR mit dem JSON-Array, kein zusätzlicher Text."""
                
                response = self.llm.invoke(prompt)
                content = response.content.strip()
                
                # Try to extract JSON from the response
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                result = json.loads(content)
                
                # Ensure result is a list
                if isinstance(result, dict):
                    result = [result]
                
                # Post-process jobs to ensure correct values
                for job in result:
                    if job.get('hasJob', False):
                        # Ensure homeOfficeOption is never null for found jobs
                        if job.get('homeOfficeOption') is None:
                            job['homeOfficeOption'] = False
                        
                        # Ensure foundOn is set to source_url if not set or is a text description
                        if not job.get('foundOn') or not job['foundOn'].startswith('http'):
                            job['foundOn'] = source_url
                
                # Filter out "no jobs found" entries from chunks after the first
                # Only the first chunk should report "no jobs found" to avoid duplicates
                if chunk_idx > 0:
                    result = [job for job in result if job.get('hasJob', False)]
                
                all_jobs.extend(result)
            
            # Filter to only jobs where hasJob is true
            all_jobs = [job for job in all_jobs if job.get('hasJob', False)]
            
            # Deduplicate jobs based on name (case-insensitive) to avoid duplicates across chunks
            seen_names = set()
            deduplicated_jobs = []
            for job in all_jobs:
                job_name = (job.get('name') or '').lower().strip()
                if job_name and job_name not in seen_names:
                    seen_names.add(job_name)
                    deduplicated_jobs.append(job)
                elif not job_name:
                    # Include jobs without names (shouldn't happen but handle gracefully)
                    deduplicated_jobs.append(job)
            
            all_jobs = deduplicated_jobs
            
            # If no jobs found in any chunk, return no jobs found message
            if not all_jobs:
                return [{
                    "hasJob": False,
                    "comments": "Keine passenden Verwaltungsstellen gefunden"
                }]
            
            logger.info(f"Successfully extracted {len(all_jobs)} job(s) for {location}")
            return all_jobs
            
        except ConnectionErrors as e:
            logger.error(f"Connection error when connecting to Ollama at {settings.OLLAMA_BASE_URL}: {str(e)}")
            logger.error("Please ensure Ollama is running")
            return [{
                "hasJob": False,
                "comments": f"Cannot connect to Ollama at {settings.OLLAMA_BASE_URL}"
            }]
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing AI response as JSON: {str(e)}")
            return [{
                "hasJob": False,
                "comments": f"Error parsing AI response: {str(e)}"
            }]
        except Exception as e:
            logger.error(f"Error analyzing content: {str(e)}")
            return [{
                "hasJob": False,
                "comments": f"Error analyzing content: {str(e)}"
            }]
    
    def extract_job_info(self, location: str, website: str, website_to_jobs: str, page_content: str) -> Dict[str, Any]:
        """
        Extract job information from website content using AI (single job - legacy method).
        
        This method is kept for backward compatibility but now delegates to extract_multiple_jobs
        and returns only the first job.
        
        Args:
            location: Location from Excel
            website: Main website URL
            website_to_jobs: Jobs page URL
            page_content: Text content from the jobs page
            
        Returns:
            Dictionary with job information
        """
        jobs = self.extract_multiple_jobs(location, website, website_to_jobs, page_content)
        # Return the first job (or default if list is empty)
        return jobs[0] if jobs else {
            "hasJob": False,
            "comments": "No jobs extracted"
        }
