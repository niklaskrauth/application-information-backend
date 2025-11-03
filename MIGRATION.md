# Migration from v1 to v2

## Overview

The application has been refactored from a general-purpose website information extraction system to a focused job extraction tool using Ollama AI for local processing.

## Key Changes

### 1. AI Provider: OpenAI → Ollama

**Before (v1):**
- Used OpenAI GPT-3.5-turbo
- Required OPENAI_API_KEY
- langchain-openai package

**After (v2):**
- Uses Ollama with LLaMA 3.1 models
- No API key required (runs locally)
- langchain-ollama package

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
- Location: `data/Landratsamt.xlsx`
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
- `ai_agent.py` - Now focuses only on job extraction with Ollama
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
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.1:8b
   EXCEL_FILE_PATH=data/Landratsamt.xlsx
   AI_RATE_LIMIT_DELAY=0
   ```

2. Install and configure Ollama:
   ```bash
   # Install Ollama (visit https://ollama.ai)
   curl -fsSL https://ollama.ai/install.sh | sh  # Linux/macOS
   
   # Start Ollama
   ollama serve
   
   # Pull model
   ollama pull llama3.1:8b
   
   # Install Python package
   pip install langchain-ollama
   ```

3. Update Excel file:
   - Create `src/data/` directory
   - Move Excel file to `data/Landratsamt.xlsx`
   - Update columns: id, location, website, websiteToJobs

4. Update frontend integration:
   ```javascript
   // Before
   fetch('http://localhost:8000/process', {method: 'POST'})
   
   // After
   fetch('http://localhost:8000/jobs')
   ```

5. Update response handling:
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
3. **Cost-Effective** - Ollama is completely free, runs locally
4. **No Rate Limits** - Local processing means unlimited requests
5. **Focused Purpose** - Specifically designed for job extraction
6. **Frontend Aligned** - Response format matches frontend interface exactly
7. **Fewer Dependencies** - Lighter installation, fewer potential issues
8. **Privacy** - All data processing happens locally

## Performance Comparison

**v1:**
- Time per entry: 30-180 seconds
- Dependencies: 20+ packages
- API costs: OpenAI usage-based
- Requires internet connection

**v2:**
- Time per entry: 10-30 seconds (8B model) or 30-120 seconds (70B model)
- Dependencies: 10 core packages
- API costs: Free (local processing)
- Works offline once model is downloaded

## Configuration

**v1 .env:**
```bash
OPENAI_API_KEY=your_openai_api_key_here
EXCEL_FILE_PATH=data/applications.xlsx
```

**v2 .env:**
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
EXCEL_FILE_PATH=data/Landratsamt.xlsx
AI_RATE_LIMIT_DELAY=0
```

## API Documentation Update

**v1:** Swagger docs showed 5 endpoints
**v2:** Swagger docs show 2 endpoints (health, jobs)

Access at: http://localhost:8000/docs
