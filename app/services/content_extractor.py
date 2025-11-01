import requests
import io
import logging
from typing import Optional
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)


class ContentExtractor:
    """Service for extracting content from PDFs and images"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def extract_pdf_content(self, url: str) -> Optional[str]:
        """
        Extract text content from a PDF URL.
        
        Args:
            url: URL to the PDF file
            
        Returns:
            Extracted text content or None if extraction fails
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            pdf_file = io.BytesIO(response.content)
            pdf_reader = PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            logger.info(f"Successfully extracted text from PDF: {url}")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting PDF content from {url}: {str(e)}")
            return None
    
    def extract_image_content(self, url: str) -> Optional[str]:
        """
        Extract text from an image using OCR.
        
        Args:
            url: URL to the image file
            
        Returns:
            Extracted text content or None if extraction fails
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            image = Image.open(io.BytesIO(response.content))
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            
            logger.info(f"Successfully extracted text from image: {url}")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting image content from {url}: {str(e)}")
            return None
