from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime


class WebsiteEntry(BaseModel):
    """Model for website entry from Excel sheet"""
    id: int
    name: str
    url: HttpUrl
    description: Optional[str] = None


class ExtractedLink(BaseModel):
    """Model for extracted links from a website"""
    url: str
    link_type: str  # 'webpage', 'pdf', 'image', 'other'
    title: Optional[str] = None


class ExtractedContent(BaseModel):
    """Model for content extracted from a URL"""
    url: str
    content_type: str
    text_content: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    extracted_at: datetime = Field(default_factory=datetime.now)


class ApplicationInfo(BaseModel):
    """Model for processed application information"""
    id: int
    name: str
    main_url: str
    description: Optional[str] = None
    extracted_links: List[ExtractedLink] = Field(default_factory=list)
    extracted_contents: List[ExtractedContent] = Field(default_factory=list)
    summary: Optional[str] = None
    processed_at: datetime = Field(default_factory=datetime.now)


class ProcessingResponse(BaseModel):
    """Model for API response"""
    success: bool
    message: str
    data: Optional[List[ApplicationInfo]] = None
    error: Optional[str] = None
