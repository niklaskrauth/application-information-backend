from langchain_groq import ChatGroq
from typing import Dict, Any
import logging
from app.config import settings
import json

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
            model="llama-3.1-70b-versatile",
            temperature=0.3,
            groq_api_key=settings.GROQ_API_KEY
        )
    
    def extract_job_info(self, location: str, website: str, website_to_jobs: str, page_content: str) -> Dict[str, Any]:
        """
        Extract job information from website content using AI.
        
        Args:
            location: Location from Excel
            website: Main website URL
            website_to_jobs: Jobs page URL
            page_content: Text content from the jobs page
            
        Returns:
            Dictionary with job information
        """
        if not self.enabled:
            return {
                "hasJob": False,
                "comments": "AI analysis disabled - Groq API key not configured"
            }
        
        try:
            prompt = f"""
You are analyzing a company's job page to extract information about available positions.

Location: {location}
Company Website: {website}
Jobs Page: {website_to_jobs}

Content from jobs page:
{page_content[:8000]}

Please analyze this content and extract the following information in JSON format:
{{
    "hasJob": true or false (whether there are any open positions),
    "name": "job title if found" or null,
    "salary": "salary information if mentioned" or null,
    "homeOfficeOption": true/false/null (whether home office or remote work is mentioned),
    "period": "work period/hours if mentioned (e.g., 'Full-time', 'Part-time', '40 hours/week')" or null,
    "employmentType": "type of employment if mentioned (e.g., 'Permanent', 'Contract', 'Internship')" or null,
    "comments": "any additional relevant information about the job or application process" or null
}}

Important:
- Set hasJob to true only if there are actual open positions
- Extract the most relevant or first job if multiple are listed
- Be concise in your extractions
- Return ONLY valid JSON, no additional text
"""
            
            response = self.llm.invoke(prompt)
            content = response.content.strip()
            
            # Try to extract JSON from the response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            logger.info(f"Successfully extracted job info for {location}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing AI response as JSON: {str(e)}")
            return {
                "hasJob": False,
                "comments": f"Error parsing AI response: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error extracting job info: {str(e)}")
            return {
                "hasJob": False,
                "comments": f"Error analyzing content: {str(e)}"
            }
