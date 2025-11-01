import logging
from typing import List
from app.models import WebsiteEntry, TableRow, Table
from app.services.excel_reader import ExcelReader
from app.services.web_scraper import WebScraper
from app.services.content_extractor import ContentExtractor
from app.services.ai_agent import AIAgent

logger = logging.getLogger(__name__)


class JobProcessor:
    """Processor for extracting job information from company websites"""
    
    def __init__(self, excel_path: str, timeout: int = 30):
        self.excel_reader = ExcelReader(excel_path)
        self.web_scraper = WebScraper(timeout=timeout)
        self.content_extractor = ContentExtractor(timeout=timeout)
        self.ai_agent = AIAgent()
    
    def process_all_jobs(self) -> Table:
        """
        Process all company entries from the Excel file and extract job information.
        
        Returns:
            Table object with job information rows (multiple rows per company if multiple jobs exist)
        """
        logger.info("Starting job processing")
        
        # Read entries from Excel
        entries = self.excel_reader.read_entries()
        logger.info(f"Found {len(entries)} entries to process")
        
        rows = []
        for entry in entries:
            try:
                # _process_single_entry now returns a list of rows
                entry_rows = self._process_single_entry(entry)
                rows.extend(entry_rows)
            except Exception as e:
                logger.error(f"Error processing entry {entry.location}: {str(e)}")
                # Create a basic row with error info
                row = TableRow(
                    location=entry.location,
                    website=entry.website,
                    websiteToJobs=entry.websiteToJobs or entry.website,
                    hasJob=False,
                    comments=f"Error processing: {str(e)}"
                )
                rows.append(row)
        
        logger.info(f"Completed processing - found {len(rows)} total job entries")
        return Table(rows=rows)
    
    def _process_single_entry(self, entry: WebsiteEntry) -> List[TableRow]:
        """
        Process a single company entry to extract job information.
        
        This method:
        1. Scrapes the main jobs page
        2. Extracts links (including PDFs and job detail pages)
        3. Follows relevant job-related links to get more content
        4. Extracts text from PDFs if found
        5. Uses AI to analyze all collected content and extract ALL jobs
        
        Args:
            entry: WebsiteEntry to process
            
        Returns:
            List of TableRow objects (one per job found)
        """
        logger.info(f"Processing entry: {entry.location}")
        
        # Determine which URL to scrape (jobs page if available, otherwise main website)
        scrape_url = entry.websiteToJobs if entry.websiteToJobs else entry.website
        
        # Scrape the jobs page
        try:
            page_text, links = self.web_scraper.scrape_website(scrape_url)
        except Exception as e:
            logger.error(f"Error scraping {scrape_url}: {str(e)}")
            return [TableRow(
                location=entry.location,
                website=entry.website,
                websiteToJobs=entry.websiteToJobs or entry.website,
                hasJob=False,
                comments=f"Error scraping website: {str(e)}"
            )]
        
        # Collect all content from main page and linked resources
        all_content = [f"Main page content:\n{page_text}"]
        
        # Process PDFs found on the jobs page (limit to first 3)
        pdf_links = [link for link in links if link.link_type == 'pdf']
        for pdf_link in pdf_links[:3]:
            logger.info(f"Extracting PDF content from: {pdf_link.url}")
            pdf_text = self.content_extractor.extract_pdf_content(pdf_link.url)
            if pdf_text:
                all_content.append(f"\nPDF content from '{pdf_link.title or pdf_link.url}':\n{pdf_text}")
        
        # Follow job-related links (limit to first 3 relevant links)
        # Look for links that might contain job details
        job_related_keywords = ['job', 'career', 'position', 'vacancy', 'opening', 'stelle', 'karriere']
        job_links = []
        
        for link in links:
            if link.link_type == 'webpage':
                link_text = (link.title or '').lower()
                link_url = link.url.lower()
                # Check if link seems job-related
                if any(keyword in link_text or keyword in link_url for keyword in job_related_keywords):
                    job_links.append(link)
        
        # Scrape content from relevant job detail pages (limit to 3)
        for job_link in job_links[:3]:
            try:
                logger.info(f"Following job link: {job_link.url}")
                linked_page_text, _ = self.web_scraper.scrape_website(job_link.url)
                all_content.append(f"\nJob detail page '{job_link.title or job_link.url}':\n{linked_page_text[:3000]}")
            except Exception as e:
                logger.warning(f"Could not scrape job link {job_link.url}: {str(e)}")
        
        # Combine all content for AI analysis
        combined_content = "\n\n".join(all_content)
        
        # Use AI to extract ALL job information from all collected content
        jobs_info_list = self.ai_agent.extract_multiple_jobs(
            location=entry.location,
            website=entry.website,
            website_to_jobs=scrape_url,
            page_content=combined_content[:15000]  # Limit total content to avoid token limits
        )
        
        # Create TableRow for each job found
        rows = []
        for job_info in jobs_info_list:
            row = TableRow(
                location=entry.location,
                website=entry.website,
                websiteToJobs=entry.websiteToJobs or entry.website,
                hasJob=job_info.get('hasJob', False),
                name=job_info.get('name'),
                salary=job_info.get('salary'),
                homeOfficeOption=job_info.get('homeOfficeOption'),
                period=job_info.get('period'),
                employmentType=job_info.get('employmentType'),
                comments=job_info.get('comments')
            )
            rows.append(row)
        
        logger.info(f"Successfully processed {entry.location}: found {len(rows)} job(s)")
        return rows
