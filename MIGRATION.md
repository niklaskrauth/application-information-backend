# Migration from v1 to v2

## Overview

The application has been refactored from a general-purpose website information extraction system to a focused job extraction tool using Groq AI.

## Key Changes

### 1. AI Provider: OpenAI → Groq

**Before:**
- Used OpenAI GPT-3.5-turbo
- Required OPENAI_API_KEY
- langchain-openai package

**After:**
- Uses Groq LLaMA 3.1 70B model
- Requires GROQ_API_KEY (free tier available)
- langchain-groq package

### 2. API Endpoints: Multiple → Single

**Before:**
- GET /health
- GET /applications
- POST /process
- POST /upload-excel

**After:**
- GET /health
- GET /jobs (main endpoint)

### 3. Data Models: General → Job-Specific

**Before:**
```python
class WebsiteEntry:
    id: int
    name: str
    url: HttpUrl
    description: Optional[str]

class ApplicationInfo:
    id: int
    name: str
    main_url: str
    extracted_links: List[ExtractedLink]
    extracted_contents: List[ExtractedContent]
    summary: Optional[str]
```

**After:**
```python
class WebsiteEntry:
    id: int
    location: str
    website: str
    websiteToJobs: Optional[str]

class TableRow:
    location: str
    website: str
    websiteToJobs: str
    hasJob: bool
    name: Optional[str]
    salary: Optional[str]
    homeOfficeOption: Optional[bool]
    period: Optional[str]
    employmentType: Optional[str]
    applicationDate: Optional[date]
    comments: Optional[str]

class Table:
    rows: List[TableRow]
```

### 4. Excel File Format

**Before:**
- Location: `data/applications.xlsx`
- Columns: id, name, url, description

**After:**
- Location: `src/data/excel.xls`
- Columns: id, location, website, websiteToJobs

### 5. Processing Pipeline

**Before:**
1. Read Excel
2. Scrape main website
3. Extract all links (PDFs, images, webpages)
4. Process PDFs (up to 5)
5. Process images with OCR (up to 3)
6. Generate AI summary

**After:**
1. Read Excel
2. Scrape jobs page (websiteToJobs or website)
3. Use AI to extract structured job information
4. Return job data in frontend format

### 6. Removed Features

- PDF text extraction
- Image OCR processing
- Content extraction from multiple sources
- Link categorization and storage
- Multiple endpoints

### 7. Dependencies Removed

- langchain-openai
- openai
- selenium
- webdriver-manager
- pdfplumber
- pillow
- pytesseract
- aiofiles

### 8. Simplified Services

**Removed:**
- `content_extractor.py` (PDF and image processing)

**Modified:**
- `ai_agent.py` - Now focuses only on job extraction with Groq
- `processor.py` - Simplified to `JobProcessor`, no PDF/image handling
- `excel_reader.py` - Updated for new column names

## Migration Steps

If migrating from v1:

1. Update `.env` file:
   ```bash
   # Replace
   OPENAI_API_KEY=...
   EXCEL_FILE_PATH=data/applications.xlsx
   
   # With
   GROQ_API_KEY=...
   EXCEL_FILE_PATH=src/data/excel.xls
   ```

2. Update Excel file:
   - Create `src/data/` directory
   - Move Excel file to `src/data/excel.xls`
   - Update columns: id, location, website, websiteToJobs

3. Update frontend integration:
   ```javascript
   // Before
   fetch('http://localhost:8000/process', {method: 'POST'})
   
   // After
   fetch('http://localhost:8000/jobs')
   ```

4. Update response handling:
   ```javascript
   // Before
   response.data.forEach(app => {
     console.log(app.name, app.summary);
   });
   
   // After
   response.rows.forEach(row => {
     console.log(row.location, row.hasJob);
   });
   ```

## Benefits of v2

1. **Simpler API** - Single endpoint, easier to use
2. **Faster Processing** - No PDF/image extraction
3. **Cost-Effective** - Groq offers generous free tier
4. **Focused Purpose** - Specifically designed for job extraction
5. **Frontend Aligned** - Response format matches frontend interface exactly
6. **Fewer Dependencies** - Lighter installation, fewer potential issues

## Performance Comparison

**v1:**
- Time per entry: 30-180 seconds
- Dependencies: 20+ packages
- API costs: OpenAI usage-based

**v2:**
- Time per entry: 5-15 seconds
- Dependencies: 10 core packages
- API costs: Groq free tier

## Configuration

**v1 .env:**
```bash
OPENAI_API_KEY=your_openai_api_key_here
EXCEL_FILE_PATH=data/applications.xlsx
```

**v2 .env:**
```bash
GROQ_API_KEY=your_groq_api_key_here
EXCEL_FILE_PATH=src/data/excel.xls
```

## API Documentation Update

**v1:** Swagger docs showed 5 endpoints
**v2:** Swagger docs show 2 endpoints (health, jobs)

Access at: http://localhost:8000/docs
