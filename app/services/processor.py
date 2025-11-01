import logging
from typing import List
from app.models import WebsiteEntry, TableRow, Table
from app.services.excel_reader import ExcelReader
from app.services.web_scraper import WebScraper
from app.services.ai_agent import AIAgent

logger = logging.getLogger(__name__)


class JobProcessor:
    """Processor for extracting job information from company websites"""
    
    def __init__(self, excel_path: str, timeout: int = 30):
        self.excel_reader = ExcelReader(excel_path)
        self.web_scraper = WebScraper(timeout=timeout)
        self.ai_agent = AIAgent()
    
    def process_all_jobs(self) -> Table:
        """
        Process all company entries from the Excel file and extract job information.
        
        Returns:
            Table object with job information rows
        """
        logger.info("Starting job processing")
        
        # Read entries from Excel
        entries = self.excel_reader.read_entries()
        logger.info(f"Found {len(entries)} entries to process")
        
        rows = []
        for entry in entries:
            try:
                row = self._process_single_entry(entry)
                rows.append(row)
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
        
        logger.info(f"Completed processing {len(rows)} entries")
        return Table(rows=rows)
    
    def _process_single_entry(self, entry: WebsiteEntry) -> TableRow:
        """
        Process a single company entry to extract job information.
        
        Args:
            entry: WebsiteEntry to process
            
        Returns:
            TableRow with job information
        """
        logger.info(f"Processing entry: {entry.location}")
        
        # Determine which URL to scrape (jobs page if available, otherwise main website)
        scrape_url = entry.websiteToJobs if entry.websiteToJobs else entry.website
        
        # Scrape the jobs page
        try:
            page_text, _ = self.web_scraper.scrape_website(scrape_url)
        except Exception as e:
            logger.error(f"Error scraping {scrape_url}: {str(e)}")
            return TableRow(
                location=entry.location,
                website=entry.website,
                websiteToJobs=entry.websiteToJobs or entry.website,
                hasJob=False,
                comments=f"Error scraping website: {str(e)}"
            )
        
        # Use AI to extract job information
        job_info = self.ai_agent.extract_job_info(
            location=entry.location,
            website=entry.website,
            website_to_jobs=scrape_url,
            page_content=page_text
        )
        
        # Create TableRow with extracted information
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
        
        logger.info(f"Successfully processed {entry.location}: hasJob={row.hasJob}")
        return row
