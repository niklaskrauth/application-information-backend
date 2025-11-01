import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Tuple
import logging
from app.models import ExtractedLink

logger = logging.getLogger(__name__)


class WebScraper:
    """Service for scraping websites and extracting links"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_website(self, url: str) -> Tuple[str, List[ExtractedLink]]:
        """
        Scrape a website and extract all links (webpages, PDFs, images).
        
        Args:
            url: The URL to scrape
            
        Returns:
            Tuple of (page_text_content, list of ExtractedLink objects)
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text content
            text_content = self._extract_text(soup)
            
            # Extract links
            links = self._extract_links(soup, url)
            
            logger.info(f"Successfully scraped {url}: found {len(links)} links")
            return text_content, links
            
        except requests.RequestException as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            raise
    
    def _extract_text(self, soup: BeautifulSoup) -> str:
        """Extract readable text from HTML"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[ExtractedLink]:
        """Extract and categorize all links from the page"""
        links = []
        seen_urls = set()
        
        # Find all anchor tags
        for tag in soup.find_all('a', href=True):
            href = tag['href']
            absolute_url = urljoin(base_url, href)
            
            # Skip if already seen
            if absolute_url in seen_urls:
                continue
            seen_urls.add(absolute_url)
            
            # Get title/text
            title = tag.get_text(strip=True) or tag.get('title', '')
            
            # Determine link type
            link_type = self._categorize_link(absolute_url)
            
            link = ExtractedLink(
                url=absolute_url,
                link_type=link_type,
                title=title if title else None
            )
            links.append(link)
        
        # Find image tags
        for img in soup.find_all('img', src=True):
            src = img['src']
            absolute_url = urljoin(base_url, src)
            
            if absolute_url in seen_urls:
                continue
            seen_urls.add(absolute_url)
            
            alt_text = img.get('alt', '')
            
            link = ExtractedLink(
                url=absolute_url,
                link_type='image',
                title=alt_text if alt_text else None
            )
            links.append(link)
        
        return links
    
    def _categorize_link(self, url: str) -> str:
        """Categorize a link by its file extension or content type"""
        url_lower = url.lower()
        
        if url_lower.endswith('.pdf'):
            return 'pdf'
        elif any(url_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']):
            return 'image'
        else:
            return 'webpage'
