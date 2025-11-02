import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from app.models import WebsiteEntry, TableRow, Table
from app.services.excel_reader import ExcelReader
from app.services.web_scraper import WebScraper
from app.services.content_extractor import ContentExtractor
from app.services.ai_agent import AIAgent

logger = logging.getLogger(__name__)


class JobProcessor:
    """Processor for extracting job information from company websites"""
    
    # Content truncation limits
    MAX_CONTENT_PER_SOURCE = 10000  # Maximum characters per content source
    
    def __init__(self, excel_path: str, timeout: int = 30):
        self.excel_reader = ExcelReader(excel_path)
        self.web_scraper = WebScraper(timeout=timeout)
        self.content_extractor = ContentExtractor(timeout=timeout)
        self.ai_agent = AIAgent()
    
    @staticmethod
    def _parse_date(date_str: str) -> Optional[date]:
        """
        Parse a date string in various formats to a date object.
        
        Args:
            date_str: Date string in format YYYY-MM-DD or similar
            
        Returns:
            date object or None if parsing fails
        """
        if not date_str:
            return None
        
        try:
            # Try ISO format first (YYYY-MM-DD)
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            try:
                # Try DD.MM.YYYY format
                return datetime.strptime(date_str, "%d.%m.%Y").date()
            except (ValueError, TypeError):
                try:
                    # Try DD/MM/YYYY format
                    return datetime.strptime(date_str, "%d/%m/%Y").date()
                except (ValueError, TypeError):
                    logger.warning(f"Could not parse date string: {date_str}")
                    return None
    
    def _create_table_row(self, entry: WebsiteEntry, job_info: Dict[str, Any], found_on: Optional[str] = None) -> TableRow:
        """
        Create a TableRow object from job information.
        
        Args:
            entry: WebsiteEntry with company information
            job_info: Dictionary with job information from AI
            found_on: Optional source information (overrides job_info['foundOn'])
            
        Returns:
            TableRow object
        """
        # Parse applicationDate if present
        application_date = None
        date_str = job_info.get('applicationDate')
        if date_str:
            application_date = self._parse_date(date_str)
        
        return TableRow(
            location=entry.location,
            website=entry.website,
            websiteToJobs=entry.websiteToJobs or entry.website,
            hasJob=job_info.get('hasJob', False),
            name=job_info.get('name'),
            salary=job_info.get('salary'),
            homeOfficeOption=job_info.get('homeOfficeOption'),
            period=job_info.get('period'),
            employmentType=job_info.get('employmentType'),
            applicationDate=application_date,
            foundOn=found_on or job_info.get('foundOn'),
            comments=job_info.get('comments')
        )
    
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
    
    def process_jobs_incrementally(self):
        """
        Process company entries one at a time and yield results incrementally.
        
        This generator processes each website sequentially:
        1. Scrapes the website
        2. Sends content to AI
        3. Yields the results
        4. Moves to the next website
        
        This approach is more efficient as it provides results immediately
        rather than waiting for all processing to complete.
        
        Yields:
            TableRow objects as they are processed
        """
        logger.info("Starting incremental job processing")
        
        # Read entries from Excel
        entries = self.excel_reader.read_entries()
        logger.info(f"Found {len(entries)} entries to process incrementally")
        
        for entry in entries:
            try:
                # Process single entry and get rows
                entry_rows = self._process_single_entry_incremental(entry)
                # Yield each row as it's produced
                for row in entry_rows:
                    yield row
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
                yield row
        
        logger.info("Completed incremental processing")
    
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
            row = self._create_table_row(entry, job_info)
            rows.append(row)
        
        logger.info(f"Successfully processed {entry.location}: found {len(rows)} job(s)")
        return rows
    
    def _process_single_entry_incremental(self, entry: WebsiteEntry) -> List[TableRow]:
        """
        Process a single company entry incrementally to extract job information.
        
        This method processes content incrementally:
        1. Scrapes the main page and sends to AI
        2. Then processes PDFs one by one
        3. Then processes job detail pages one by one
        
        Each piece of content is analyzed separately and results are yielded immediately.
        
        Args:
            entry: WebsiteEntry to process
            
        Returns:
            List of TableRow objects (one per job found)
        """
        logger.info(f"Processing entry incrementally: {entry.location}")
        
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
        
        all_rows = []
        
        # First, process main page content
        # Note: Main page results include all jobs (hasJob=true or false) to indicate
        # if no jobs were found. PDFs and detail pages only add jobs when hasJob=true
        # to avoid duplicate "no jobs found" entries.
        logger.info(f"Processing main page for {entry.location}")
        main_page_content = f"Main page content:\n{page_text[:self.MAX_CONTENT_PER_SOURCE]}"
        
        jobs_info_list = self.ai_agent.extract_multiple_jobs(
            location=entry.location,
            website=entry.website,
            website_to_jobs=scrape_url,
            page_content=main_page_content
        )
        
        # Convert jobs to TableRow objects (including hasJob=false entries from main page)
        for job_info in jobs_info_list:
            row = self._create_table_row(entry, job_info, found_on='Main page')
            all_rows.append(row)
        
        # Process PDFs one by one (limit to first 2 for efficiency)
        pdf_links = [link for link in links if link.link_type == 'pdf']
        for pdf_link in pdf_links[:2]:
            logger.info(f"Processing PDF: {pdf_link.url}")
            try:
                pdf_text = self.content_extractor.extract_pdf_content(pdf_link.url)
                if pdf_text:
                    pdf_content = f"PDF content from '{pdf_link.title or pdf_link.url}':\n{pdf_text[:self.MAX_CONTENT_PER_SOURCE]}"
                    
                    jobs_info_list = self.ai_agent.extract_multiple_jobs(
                        location=entry.location,
                        website=entry.website,
                        website_to_jobs=scrape_url,
                        page_content=pdf_content
                    )
                    
                    for job_info in jobs_info_list:
                        if job_info.get('hasJob', False):  # Only add if job was found
                            row = self._create_table_row(
                                entry, 
                                job_info, 
                                found_on=f"PDF: {pdf_link.title or 'document'}"
                            )
                            all_rows.append(row)
            except Exception as e:
                logger.warning(f"Could not process PDF {pdf_link.url}: {str(e)}")
        
        # Process job detail pages one by one (limit to first 2 for efficiency)
        job_related_keywords = ['job', 'career', 'position', 'vacancy', 'opening', 'stelle', 'karriere']
        job_links = []
        
        for link in links:
            if link.link_type == 'webpage':
                link_text = (link.title or '').lower()
                link_url = link.url.lower()
                if any(keyword in link_text or keyword in link_url for keyword in job_related_keywords):
                    job_links.append(link)
        
        for job_link in job_links[:2]:
            logger.info(f"Processing job detail page: {job_link.url}")
            try:
                linked_page_text, _ = self.web_scraper.scrape_website(job_link.url)
                page_content = f"Job detail page '{job_link.title or job_link.url}':\n{linked_page_text[:self.MAX_CONTENT_PER_SOURCE]}"
                
                jobs_info_list = self.ai_agent.extract_multiple_jobs(
                    location=entry.location,
                    website=entry.website,
                    website_to_jobs=scrape_url,
                    page_content=page_content
                )
                
                for job_info in jobs_info_list:
                    if job_info.get('hasJob', False):  # Only add if job was found
                        row = self._create_table_row(
                            entry,
                            job_info,
                            found_on=f"Page: {job_link.title or job_link.url}"
                        )
                        all_rows.append(row)
            except Exception as e:
                logger.warning(f"Could not process job link {job_link.url}: {str(e)}")
        
        # If no jobs were found at all, add a no-jobs-found entry
        if not all_rows or not any(row.hasJob for row in all_rows):
            all_rows = [TableRow(
                location=entry.location,
                website=entry.website,
                websiteToJobs=entry.websiteToJobs or entry.website,
                hasJob=False,
                comments="No jobs found"
            )]
        
        logger.info(f"Successfully processed {entry.location} incrementally: found {len(all_rows)} job(s)")
        return all_rows
