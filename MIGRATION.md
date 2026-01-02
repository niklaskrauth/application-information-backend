# Migration from v1 to v2 to v3

## Overview

The application has evolved from OpenAI to Ollama, and now to Hugging Face with German language models for enhanced local processing and German-specific optimization.

## Latest Changes (v3): Ollama → Hugging Face

### AI Provider: Ollama → Hugging Face

**Before (v2):**
- Used Ollama with LLaMA 3.1 models
- Required Ollama server running
- langchain-ollama package

**After (v3):**
- Uses Hugging Face with German-optimized models
- No external server required
- langchain-huggingface, transformers, sentence-transformers packages
- Specifically uses German language models:
  - **Text Generation**: Veronika-T/mistral-german-7b
  - **Embeddings**: deutsche-telekom/gbert-large-paraphrase-cosine

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

## Migration Steps (v2 → v3)

If migrating from v2 (Ollama):

1. Update `.env` file:
   ```bash
   # Remove
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3.1:8b
   
   # Add
   HUGGINGFACE_MODEL=Veronika-T/mistral-german-7b
   HUGGINGFACE_EMBEDDING_MODEL=deutsche-telekom/gbert-large-paraphrase-cosine
   HUGGINGFACE_API_TOKEN=
   ```

2. Update dependencies:
   ```bash
   pip uninstall langchain-ollama
   pip install langchain-huggingface transformers sentence-transformers torch
   # Or simply
   pip install -r requirements.txt
   ```

3. Remove Ollama (optional):
   ```bash
   # You can now uninstall Ollama if not needed elsewhere
   # No Ollama server needs to be running
   ```

4. First run will download models:
   - Models are cached in `~/.cache/huggingface/`
   - Approximately 15-20GB total download
   - This happens once, subsequent runs use cached models

## Migration Steps (v1 → v3)

If migrating directly from v1:

1. Update `.env` file:
   ```bash
   # Replace
   OPENAI_API_KEY=...
   EXCEL_FILE_PATH=data/applications.xlsx
   
   # With
   HUGGINGFACE_MODEL=Veronika-T/mistral-german-7b
   HUGGINGFACE_EMBEDDING_MODEL=deutsche-telekom/gbert-large-paraphrase-cosine
   HUGGINGFACE_API_TOKEN=
   EXCEL_FILE_PATH=data/Landratsamt.xlsx
   ```

2. Install Hugging Face dependencies:
   ```bash
   pip install langchain-huggingface transformers sentence-transformers torch
   # Or
   pip install -r requirements.txt
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

## Benefits of v3

1. **German Language Optimized** - Uses models specifically trained for German text
2. **No External Server** - Everything runs in Python process, no Ollama server needed
3. **Simpler Setup** - Just install Python packages, no additional software
4. **Cost-Effective** - Hugging Face models are free, runs locally
5. **No Rate Limits** - Local processing means unlimited requests
6. **Focused Purpose** - Specifically designed for German job extraction
7. **Frontend Aligned** - Response format matches frontend interface exactly
8. **Privacy** - All data processing happens locally
9. **Better German Understanding** - Dedicated German models vs multilingual

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
- Requires Ollama server running

**v3:**
- Time per entry: 10-60 seconds (depends on hardware)
- Dependencies: 12 core packages
- API costs: Free (local processing)
- Works offline once models are downloaded
- No external server required
- Optimized for German language

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

**v3 .env:**
```bash
HUGGINGFACE_MODEL=Veronika-T/mistral-german-7b
HUGGINGFACE_EMBEDDING_MODEL=deutsche-telekom/gbert-large-paraphrase-cosine
HUGGINGFACE_API_TOKEN=
EXCEL_FILE_PATH=data/Landratsamt.xlsx
```

## API Documentation Update

**v1:** Swagger docs showed 5 endpoints
**v2:** Swagger docs show 2 endpoints (health, jobs)

Access at: http://localhost:8000/docs
