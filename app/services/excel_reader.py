import pandas as pd
from typing import List
import logging
from app.models import WebsiteEntry

logger = logging.getLogger(__name__)


class ExcelReader:
    """Service for reading website entries from Excel files"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def read_entries(self) -> List[WebsiteEntry]:
        """
        Read website entries from Excel file.
        
        Expected columns:
        - id: Unique identifier
        - location: Company location
        - website: Main website URL
        - websiteToJobs: Jobs page URL (optional)
        
        Returns:
            List of WebsiteEntry objects
        """
        try:
            # Read Excel file
            df = pd.read_excel(self.file_path)
            
            # Validate required columns
            required_columns = ['id', 'location', 'website']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Convert to WebsiteEntry objects
            entries = []
            for _, row in df.iterrows():
                entry_data = {
                    'id': int(row['id']),
                    'location': str(row['location']),
                    'website': str(row['website']),
                }
                
                # Add optional websiteToJobs if present
                if 'websiteToJobs' in df.columns and pd.notna(row['websiteToJobs']):
                    entry_data['websiteToJobs'] = str(row['websiteToJobs'])
                
                entry = WebsiteEntry(**entry_data)
                entries.append(entry)
            
            logger.info(f"Successfully read {len(entries)} entries from Excel file")
            return entries
            
        except FileNotFoundError:
            logger.error(f"Excel file not found: {self.file_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading Excel file: {str(e)}")
            raise
