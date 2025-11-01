from langchain_groq import ChatGroq
from typing import Dict, Any, List
import logging
from app.config import settings
import json
import time

logger = logging.getLogger(__name__)

# Job types to exclude from results (trainee, internship, student positions)
EXCLUDED_JOB_TYPES = [
    "Auszubildung", "Auszubildende", "Auszubildender", "Azubi",
    "Praktikum", "Praktikant", "Praktikanten", "Praktikantin",
    "Studium", "Student", "Studenten", "Studentin", "Studentische"
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
    """LangChain AI Agent using Groq for analyzing job information from websites"""
    
    def __init__(self):
        if not settings.GROQ_API_KEY:
            logger.warning("Groq API key not set. AI analysis will be disabled.")
            self.enabled = False
            return
        
        self.enabled = True
        self.llm = ChatGroq(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0.3,
            groq_api_key=settings.GROQ_API_KEY
        )
        # Initialize to current time to avoid artificial delay on first call
        self.last_api_call_time = time.time()
        self.min_delay_between_calls = settings.AI_RATE_LIMIT_DELAY  # configurable delay
        # Maximum content length to send to AI (tokens limit consideration)
        self.max_content_length = 10000
    
    def _rate_limit(self):
        """Implement rate limiting by adding delays between API calls"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call_time
        
        if time_since_last_call < self.min_delay_between_calls:
            sleep_time = self.min_delay_between_calls - time_since_last_call
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_api_call_time = time.time()
    
    def extract_multiple_jobs(self, location: str, website: str, website_to_jobs: str, page_content: str) -> List[Dict[str, Any]]:
        """
        Extract ALL job information from website content using AI.
        Returns a list of job dictionaries, one for each job found.
        
        Args:
            location: Location from Excel
            website: Main website URL
            website_to_jobs: Jobs page URL
            page_content: Text content from the jobs page
            
        Returns:
            List of dictionaries with job information (one per job)
        """
        if not self.enabled:
            return [{
                "hasJob": False,
                "comments": "AI analysis disabled - Groq API key not configured"
            }]
        
        try:
            # Apply rate limiting
            self._rate_limit()
            
            # Build exclusion and inclusion lists for prompt
            excluded_terms = '", "'.join(EXCLUDED_JOB_TYPES)
            included_terms = '", "'.join(INCLUDED_JOB_TYPES)
            excluded_qualifications = '", "'.join(EXCLUDED_QUALIFICATIONS)
            
            prompt = f"""
Sie analysieren eine Unternehmenswebseite, um Informationen über ALLE verfügbaren Verwaltungsstellen zu extrahieren.

Standort: {location}
Unternehmenswebseite: {website}
Stellenseite: {website_to_jobs}

Inhalt der Stellenseite:
{page_content[:self.max_content_length]}

Bitte analysieren Sie diesen Inhalt und extrahieren Sie Informationen für ALLE gefundenen Stellenangebote. Geben Sie ein JSON-Array zurück, wobei jedes Element eine Stelle repräsentiert:
[
    {{
        "hasJob": true,
        "name": "Stellentitel",
        "salary": "Gehaltsinformationen falls erwähnt" oder null,
        "homeOfficeOption": true/false/null (ob Home Office oder Remote-Arbeit erwähnt wird),
        "period": "Arbeitszeit falls erwähnt (z.B., 'Vollzeit', 'Teilzeit', '40 Stunden/Woche')" oder null,
        "employmentType": "Beschäftigungsart falls erwähnt (z.B., 'Unbefristet', 'Befristet', 'Festanstellung')" oder null,
        "applicationDate": "JJJJ-MM-TT Format (z.B., '2025-12-31') falls eine Bewerbungsfrist oder ein Datum erwähnt wird" oder null,
        "foundOn": "Quelle der Stelle (z.B., 'Hauptseite', 'PDF: [Titel]', 'Unterseite: [URL]')" oder null,
        "comments": "zusätzliche relevante Informationen zu dieser spezifischen Stelle (KEINE Datumsangaben hier)" oder null
    }},
    ... (ein Eintrag für jede gefundene Stelle)
]

WICHTIGE FILTERKRITERIEN - Eine Stelle wird NUR extrahiert, wenn:
1. Sie ist eine Verwaltungs- oder Bürostelle (z.B., "{included_terms}")
2. Sie enthält NICHT die Begriffe: "{excluded_terms}"
3. Sie erfordert KEINE höhere Ausbildung wie: "{excluded_qualifications}"
4. Sie ist für Personen mit Berufsausbildung oder vergleichbarer Qualifikation geeignet

WICHTIG zum Datum (applicationDate):
- Wenn eine Bewerbungsfrist erwähnt wird (z.B., "Bewerbung bis 31.12.2025"), extrahieren Sie das Datum im Format JJJJ-MM-TT
- Wenn "bis Ende des Monats" oder ähnlich steht, berechnen Sie das konkrete Datum
- Fügen Sie Datumsangaben NIEMALS in das "comments" Feld ein
- Nur wenn kein Datum vorhanden ist, setzen Sie applicationDate auf null

WICHTIG zur Quelle (foundOn):
- Identifizieren Sie, wo die Stelle gefunden wurde (z.B., auf der Hauptseite, in einem PDF-Dokument, auf einer Unterseite)
- Geben Sie eine beschreibende Quelle an (z.B., "Hauptseite", "PDF: Stellenanzeige.pdf", "Unterseite: https://...")
- Wenn die Quelle unklar ist, setzen Sie foundOn auf null

Weitere wichtige Regeln:
- Extrahieren Sie ALLE passenden Stellen, die auf der Seite gefunden werden
- Wenn KEINE passenden Stellen gefunden werden, geben Sie zurück: [{{"hasJob": false, "comments": "Keine passenden Verwaltungsstellen gefunden"}}]
- Jede Stelle sollte ein separates Objekt im Array sein
- Seien Sie präzise in Ihren Extraktionen
- Geben Sie NUR ein gültiges JSON-Array zurück, keinen zusätzlichen Text
- Alle Textfelder sollten auf Deutsch sein
"""
            
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
                # If AI returned a single job as dict, wrap it in a list
                result = [result]
            
            logger.info(f"Successfully extracted {len(result)} job(s) for {location}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing AI response as JSON: {str(e)}")
            return [{
                "hasJob": False,
                "comments": f"Error parsing AI response: {str(e)}"
            }]
        except Exception as e:
            logger.error(f"Error extracting job info: {str(e)}")
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
