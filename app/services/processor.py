import logging
from typing import List
from datetime import datetime
from app.models import WebsiteEntry, ApplicationInfo, ExtractedContent
from app.services.excel_reader import ExcelReader
from app.services.web_scraper import WebScraper
from app.services.content_extractor import ContentExtractor
from app.services.ai_agent import AIAgent

logger = logging.getLogger(__name__)


class ApplicationProcessor:
    """Main processor for handling website applications"""
    
    def __init__(self, excel_path: str, timeout: int = 30):
        self.excel_reader = ExcelReader(excel_path)
        self.web_scraper = WebScraper(timeout=timeout)
        self.content_extractor = ContentExtractor(timeout=timeout)
        self.ai_agent = AIAgent()
    
    def process_all_applications(self) -> List[ApplicationInfo]:
        """
        Process all applications from the Excel file.
        
        Returns:
            List of ApplicationInfo objects with extracted data
        """
        logger.info("Starting application processing")
        
        # Read entries from Excel
        entries = self.excel_reader.read_entries()
        logger.info(f"Found {len(entries)} entries to process")
        
        results = []
        for entry in entries:
            try:
                app_info = self._process_single_application(entry)
                results.append(app_info)
            except Exception as e:
                logger.error(f"Error processing application {entry.name}: {str(e)}")
                # Create a basic entry with error info
                app_info = ApplicationInfo(
                    id=entry.id,
                    name=entry.name,
                    main_url=str(entry.url),
                    description=entry.description,
                    summary=f"Error processing: {str(e)}"
                )
                results.append(app_info)
        
        logger.info(f"Completed processing {len(results)} applications")
        return results
    
    def _process_single_application(self, entry: WebsiteEntry) -> ApplicationInfo:
        """
        Process a single website application entry.
        
        Args:
            entry: WebsiteEntry to process
            
        Returns:
            ApplicationInfo with all extracted data
        """
        logger.info(f"Processing application: {entry.name}")
        
        # Scrape the main website
        main_text, links = self.web_scraper.scrape_website(str(entry.url))
        
        # Store main page content
        extracted_contents = [
            ExtractedContent(
                url=str(entry.url),
                content_type='webpage',
                text_content=main_text,
                metadata={'is_main_page': True}
            )
        ]
        
        # Process PDFs and images from extracted links
        pdf_count = 0
        image_count = 0
        
        for link in links:
            if link.link_type == 'pdf' and pdf_count < 5:  # Limit to first 5 PDFs
                pdf_text = self.content_extractor.extract_pdf_content(link.url)
                if pdf_text:
                    extracted_contents.append(
                        ExtractedContent(
                            url=link.url,
                            content_type='pdf',
                            text_content=pdf_text,
                            metadata={'title': link.title}
                        )
                    )
                    pdf_count += 1
            
            elif link.link_type == 'image' and image_count < 3:  # Limit to first 3 images
                image_text = self.content_extractor.extract_image_content(link.url)
                if image_text:
                    extracted_contents.append(
                        ExtractedContent(
                            url=link.url,
                            content_type='image',
                            text_content=image_text,
                            metadata={'title': link.title, 'alt': link.title}
                        )
                    )
                    image_count += 1
        
        # Generate AI summary
        analysis_data = {
            'name': entry.name,
            'url': str(entry.url),
            'description': entry.description,
            'num_links': len(links),
            'num_pdfs': sum(1 for l in links if l.link_type == 'pdf'),
            'num_images': sum(1 for l in links if l.link_type == 'image'),
            'sample_content': main_text[:2000] if main_text else ''
        }
        
        summary = self.ai_agent.analyze_application_info(analysis_data)
        
        # Create ApplicationInfo object
        app_info = ApplicationInfo(
            id=entry.id,
            name=entry.name,
            main_url=str(entry.url),
            description=entry.description,
            extracted_links=links,
            extracted_contents=extracted_contents,
            summary=summary,
            processed_at=datetime.now()
        )
        
        logger.info(f"Successfully processed {entry.name}: {len(links)} links, {len(extracted_contents)} contents")
        return app_info
