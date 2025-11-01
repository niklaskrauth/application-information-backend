from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from typing import List, Dict, Any
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class AIAgent:
    """LangChain AI Agent for analyzing and summarizing website content"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not set. AI summarization will be disabled.")
            self.enabled = False
            return
        
        self.enabled = True
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY
        )
    
    def summarize_content(self, content: str, context: str = "") -> str:
        """
        Summarize extracted content using AI.
        
        Args:
            content: The text content to summarize
            context: Additional context about the content
            
        Returns:
            AI-generated summary
        """
        if not self.enabled:
            return "AI summarization disabled - OpenAI API key not configured"
        
        try:
            prompt = f"""
            Please provide a concise summary of the following content from a website application.
            {f'Context: {context}' if context else ''}
            
            Content:
            {content[:5000]}  # Limit content length
            
            Summary should include:
            - Main purpose or topic
            - Key features or information
            - Any important details
            """
            
            response = self.llm.invoke(prompt)
            summary = response.content
            
            logger.info("Successfully generated content summary")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return f"Error generating summary: {str(e)}"
    
    def analyze_application_info(self, data: Dict[str, Any]) -> str:
        """
        Analyze all extracted information about an application.
        
        Args:
            data: Dictionary containing all extracted data
            
        Returns:
            Comprehensive analysis and summary
        """
        if not self.enabled:
            return "AI analysis disabled - OpenAI API key not configured"
        
        try:
            prompt = f"""
            Analyze the following information extracted from a website application:
            
            Application Name: {data.get('name', 'Unknown')}
            Main URL: {data.get('url', 'Unknown')}
            Description: {data.get('description', 'Not provided')}
            
            Number of links found: {data.get('num_links', 0)}
            Number of PDFs: {data.get('num_pdfs', 0)}
            Number of images: {data.get('num_images', 0)}
            
            Sample content:
            {data.get('sample_content', 'No content available')[:3000]}
            
            Please provide:
            1. A brief overview of what this application/website is about
            2. Key information or features identified
            3. Summary of the available resources (PDFs, images, etc.)
            """
            
            response = self.llm.invoke(prompt)
            analysis = response.content
            
            logger.info("Successfully generated application analysis")
            return analysis
            
        except Exception as e:
            logger.error(f"Error generating analysis: {str(e)}")
            return f"Error generating analysis: {str(e)}"
