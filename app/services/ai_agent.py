from langchain_groq import ChatGroq
from typing import Dict, Any, List
import logging
from app.config import settings
import json
import time

logger = logging.getLogger(__name__)


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
        self.last_api_call_time = 0
        self.min_delay_between_calls = settings.AI_RATE_LIMIT_DELAY  # configurable delay
    
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
            
            prompt = f"""
You are analyzing a company's job page to extract information about ALL available positions.

Location: {location}
Company Website: {website}
Jobs Page: {website_to_jobs}

Content from jobs page:
{page_content[:10000]}

Please analyze this content and extract information for ALL job positions found. Return a JSON array where each element represents one job:
[
    {{
        "hasJob": true,
        "name": "job title",
        "salary": "salary information if mentioned" or null,
        "homeOfficeOption": true/false/null (whether home office or remote work is mentioned),
        "period": "work period/hours if mentioned (e.g., 'Full-time', 'Part-time', '40 hours/week')" or null,
        "employmentType": "type of employment if mentioned (e.g., 'Permanent', 'Contract', 'Internship')" or null,
        "comments": "any additional relevant information about this specific job" or null
    }},
    ... (one entry for each job found)
]

Important:
- Extract ALL jobs found on the page, not just the first one
- If NO jobs are found, return: [{{"hasJob": false, "comments": "No open positions found"}}]
- Each job should be a separate object in the array
- Be concise in your extractions
- Return ONLY valid JSON array, no additional text
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
