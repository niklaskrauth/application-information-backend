from typing import Dict, Any, List, Optional
import logging
from app.config import settings
import json
import time

logger = logging.getLogger(__name__)

# Import Hugging Face and handle connection errors
try:
    from langchain_huggingface import HuggingFacePipeline, HuggingFaceEmbeddings
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
except ImportError:
    HuggingFacePipeline = None
    HuggingFaceEmbeddings = None
    logger.warning("langchain-huggingface or transformers is not installed. Install them with: pip install langchain-huggingface transformers sentence-transformers")

# Build tuple of connection error types to handle
def _get_connection_errors():
    """Get tuple of connection error types based on available libraries"""
    errors = [ConnectionRefusedError, ConnectionError, OSError, RuntimeError]
    
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
    """LangChain AI Agent using Hugging Face for analyzing job information from websites"""
    
    # Configuration constants
    MAX_CHUNK_LENGTH = 12000  # Characters per chunk for processing
    
    def __init__(self):
        self.provider = "huggingface"
        self.enabled = False
        self.llm: Optional[Any] = None
        self.embeddings: Optional[Any] = None
        
        if HuggingFacePipeline is None or HuggingFaceEmbeddings is None:
            logger.error("Hugging Face provider requires langchain-huggingface and transformers. Install them with: pip install langchain-huggingface transformers sentence-transformers")
            return
        
        try:
            self.enabled = True
            
            # Initialize German text generation model
            logger.info(f"Initializing German text generation model: {settings.HUGGINGFACE_MODEL}")
            tokenizer = AutoTokenizer.from_pretrained(
                settings.HUGGINGFACE_MODEL,
                token=settings.HUGGINGFACE_API_TOKEN if settings.HUGGINGFACE_API_TOKEN else None
            )
            
            # Try GPU first, fall back to CPU if GPU memory is insufficient
            try:
                model = AutoModelForCausalLM.from_pretrained(
                    settings.HUGGINGFACE_MODEL,
                    device_map="auto",
                    token=settings.HUGGINGFACE_API_TOKEN if settings.HUGGINGFACE_API_TOKEN else None
                )
                logger.info("Text generation model loaded with GPU acceleration")
            except (RuntimeError, OSError) as e:
                logger.warning(f"Failed to load model with GPU (device_map='auto'): {str(e)}")
                logger.info("Falling back to CPU-only mode for text generation")
                model = AutoModelForCausalLM.from_pretrained(
                    settings.HUGGINGFACE_MODEL,
                    device_map="cpu",
                    token=settings.HUGGINGFACE_API_TOKEN if settings.HUGGINGFACE_API_TOKEN else None
                )
            
            text_generation_pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=2048,
                temperature=0.1,
                do_sample=True,
                top_p=0.95,
                repetition_penalty=1.15
            )
            
            self.llm = HuggingFacePipeline(pipeline=text_generation_pipeline)
            
            # Initialize German embedding model (using same device strategy for consistency)
            logger.info(f"Initializing German embedding model: {settings.HUGGINGFACE_EMBEDDING_MODEL}")
            # Check if CUDA is available before trying to use GPU
            try:
                import torch
                use_gpu = torch.cuda.is_available()
            except ImportError:
                use_gpu = False
            
            if use_gpu:
                try:
                    self.embeddings = HuggingFaceEmbeddings(
                        model_name=settings.HUGGINGFACE_EMBEDDING_MODEL,
                        model_kwargs={'device': 'cuda'},
                        encode_kwargs={'normalize_embeddings': True}
                    )
                    logger.info("Embedding model loaded with GPU acceleration")
                except (RuntimeError, OSError) as e:
                    logger.warning(f"Failed to load embeddings with GPU: {str(e)}")
                    logger.info("Falling back to CPU for embeddings")
                    self.embeddings = HuggingFaceEmbeddings(
                        model_name=settings.HUGGINGFACE_EMBEDDING_MODEL,
                        model_kwargs={'device': 'cpu'},
                        encode_kwargs={'normalize_embeddings': True}
                    )
            else:
                logger.info("GPU not available, using CPU for embeddings")
                self.embeddings = HuggingFaceEmbeddings(
                    model_name=settings.HUGGINGFACE_EMBEDDING_MODEL,
                    model_kwargs={'device': 'cpu'},
                    encode_kwargs={'normalize_embeddings': True}
                )
            
            logger.info(f"AI Agent initialized with Hugging Face provider (model: {settings.HUGGINGFACE_MODEL}, embeddings: {settings.HUGGINGFACE_EMBEDDING_MODEL})")
        except Exception as e:
            logger.warning(f"Failed to initialize Hugging Face: {str(e)}. AI agent will be disabled. Make sure you have enough memory and the models can be downloaded.")
            self.enabled = False
            return
        
        # Initialize to current time to avoid artificial delay on first call
        self.last_api_call_time = time.time()
        self.min_delay_between_calls = 0  # No rate limiting for local Hugging Face
        # Set reasonable content length for chunking
        self.max_chunk_length = self.MAX_CHUNK_LENGTH
    
    def _rate_limit(self):
        """Implement rate limiting by adding delays between API calls"""
        # No rate limiting for Hugging Face - removed delay
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
                "comments": "AI analysis disabled - langchain-huggingface or transformers not installed or models not available"
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
                
                prompt = f"""Analysieren Sie den folgenden Text und extrahieren Sie alle relevanten Verwaltungs- und Bürostellen.

WICHTIG: "Stellenausschreiben", "Stellenangebote", "Karriere", "Jobs" sind Überschriften/Seitentitel - NICHT als Stellentitel extrahieren! Suchen Sie nach den tatsächlichen Stellentiteln UNTER diesen Überschriften.

Standort: {location}
Heutiges Datum: {current_date}
Quelle URL: {source_url}

Text:
{chunk}

FILTERREGELN - Extrahieren Sie Stellen die folgende Kriterien erfüllen:
1. Die Stelle ist eine Verwaltungs-, Büro- oder Sachbearbeiterstelle
2. Beispiele für PASSENDE Stellen: "{included_terms}"
3. AUSSCHLIESSEN: "{excluded_terms}"
4. KEINE Führungspositionen (Leiter, Manager, Direktor, Abteilungsleiter)
5. KEINE Stellen die zwingend Hochschulabschluss (Bachelor/Master/Diplom) erfordern

WICHTIG FÜR FILTERUNG:
- Seien Sie NICHT zu streng - im Zweifel eher extrahieren als ignorieren
- Wenn eine Stelle Verwaltungsaufgaben hat, ist sie relevant
- Stellenausschreibungen ohne explizite Titel aber mit Verwaltungsbezug sind OK
- Auch Stellen mit Ausbildungsabschluss + Berufserfahrung extrahieren

Geben Sie ein JSON-Array zurück. Jedes Element repräsentiert EINE gefundene Stelle.

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
    "foundOn": "{source_url}",
    "comments": "Zusätzliche relevante Informationen (z.B. Voraussetzungen, besondere Hinweise)" oder null
  }}
]


=== WICHTIG: SALARY FELD (HÖCHSTE PRIORITÄT) ===
Das salary Feld ist sehr wichtig! Suchen Sie gründlich nach Gehaltsinformationen im GESAMTEN Text!

Suchen Sie nach diesen Begriffen IM GESAMTEN TEXT:
- "Entgeltgruppe" + Zahl (z.B. "Entgeltgruppe 6" → "EG 6")
- "EG" + Zahl (z.B. "EG 9a" → "EG 9a")
- "TVöD", "TVÖD", "TV-L", "TVL" (mit oder ohne EG/E)
- "Besoldungsgruppe" oder "BesGr" + Buchstabe/Zahl (z.B. "A 9" → "A 9")
- "E" + Zahl (z.B. "E 9b" → "E 9b")
- Auch Formulierungen wie "nach", "bis zu", "Vergütung", "Entlohnung"

BEISPIELE:
- "Die Vergütung erfolgt nach Entgeltgruppe 6 TVöD" → salary: "EG 6 TVöD"
- "bis EG 9a" → salary: "bis EG 9a"
- "TVöD E 9b" → salary: "TVöD E 9b"
- "Besoldungsgruppe A 10" → salary: "A 10"
- "Vergütung nach TVöD" → salary: "TVöD"

STRATEGIE: Lesen Sie den Text ZWEIMAL durch nur um nach salary zu suchen!

=== HINWEISE: occupyStart ===
Suchen Sie nach Eintrittsdatum:
- "ab sofort" oder "nächstmöglich" → {current_date}
- "zum 01.01.2025" → "2025-01-01"
- "ab 15.03.2025" → "2025-03-15"

=== HINWEISE: foundOn ===
- foundOn muss die URL sein: {source_url}
- Niemals Text wie "Main page" oder "PDF: filename"
- Verwenden Sie immer: {source_url}

=== FILTERHINWEISE ===
- NICHT extrahieren: Ausbildung/Praktikum/Student/Manager/Leiter/Direktor
- Im Zweifel: Verwaltungsstelle → extrahieren!
- "Stellenausschreiben"/"Stellenangebote" sind keine Stellentitel, nur Überschriften
- Wenn keine Stelle gefunden: [{{"hasJob": false, "comments": "Keine passenden Verwaltungsstellen gefunden"}}]

Antworten Sie NUR mit dem JSON-Array, kein zusätzlicher Text."""
                
                response = self.llm.invoke(prompt)
                # HuggingFacePipeline returns a string directly
                if isinstance(response, str):
                    content = response.strip()
                else:
                    # Handle case where response might be an object with content attribute
                    content = getattr(response, 'content', str(response)).strip()
                
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
                        found_on_value = job.get('foundOn', '')
                        if not found_on_value or not isinstance(found_on_value, str) or not found_on_value.startswith('http'):
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
            logger.error(f"Connection error when loading Hugging Face models: {str(e)}")
            logger.error("Please ensure you have enough memory and internet connection to download models")
            return [{
                "hasJob": False,
                "comments": f"Cannot load Hugging Face models: {str(e)}"
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
