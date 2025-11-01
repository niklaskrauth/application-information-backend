from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime, date


class WebsiteEntry(BaseModel):
    """Model for website entry from Excel sheet"""
    id: int
    location: str
    website: str
    websiteToJobs: Optional[str] = None


class ExtractedLink(BaseModel):
    """Model for extracted links from a website"""
    url: str
    link_type: str  # 'webpage', 'pdf', 'image', 'other'
    title: Optional[str] = None


class TableRow(BaseModel):
    """Model for job application row matching frontend interface"""
    location: str
    website: str
    websiteToJobs: str
    hasJob: bool
    foundAt: Optional[str] = None
    
    name: Optional[str] = None
    salary: Optional[str] = None
    homeOfficeOption: Optional[bool] = None
    period: Optional[str] = None
    employmentType: Optional[str] = None
    applicationDate: Optional[date] = None
    comments: Optional[str] = None


class Table(BaseModel):
    """Model for table response matching frontend interface"""
    rows: List[TableRow]


class ProcessingResponse(BaseModel):
    """Model for API response"""
    success: bool
    message: str
    data: Optional[Table] = None
    error: Optional[str] = None
