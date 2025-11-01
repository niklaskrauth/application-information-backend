# Architecture Overview

This document provides a detailed overview of the Application Information Backend architecture.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Application                     │
│                     (React, Vue, Angular, etc.)                  │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP/JSON
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI REST API                            │
│                    (app/main.py)                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ GET /health  │  │ GET /apps    │  │ POST /process│          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Application Processor                          │
│                  (app/services/processor.py)                     │
│                                                                   │
│  Orchestrates the entire processing pipeline                     │
└───┬──────────────────┬──────────────────┬─────────────────────┬─┘
    │                  │                  │                     │
    ▼                  ▼                  ▼                     ▼
┌─────────┐    ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  Excel  │    │     Web      │   │   Content    │   │  AI Agent    │
│ Reader  │    │   Scraper    │   │  Extractor   │   │ (LangChain)  │
└─────────┘    └──────────────┘   └──────────────┘   └──────────────┘
     │                 │                  │                     │
     │                 │                  │                     │
     ▼                 ▼                  ▼                     ▼
┌─────────┐    ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  Excel  │    │   Websites   │   │  PDFs/Images │   │   OpenAI     │
│  File   │    │              │   │              │   │   GPT-3.5    │
└─────────┘    └──────────────┘   └──────────────┘   └──────────────┘
```

## Component Details

### 1. FastAPI Application (app/main.py)

**Purpose:** RESTful API server that handles HTTP requests from the frontend.

**Key Features:**
- CORS middleware for cross-origin requests
- Multiple endpoints for different operations
- File upload handling
- Error handling and logging

**Dependencies:**
- FastAPI for web framework
- Uvicorn as ASGI server
- Pydantic for request/response validation

### 2. Excel Reader (app/services/excel_reader.py)

**Purpose:** Read and parse Excel files containing website application data.

**Input:**
- Excel file (.xlsx) with columns: id, name, url, description

**Output:**
- List of WebsiteEntry objects

**Key Features:**
- Validation of required columns
- Type conversion and error handling
- Support for optional fields

**Dependencies:**
- pandas for Excel reading
- openpyxl as Excel engine

### 3. Web Scraper (app/services/web_scraper.py)

**Purpose:** Scrape websites and extract links and content.

**Input:**
- Website URL

**Output:**
- Text content from the page
- List of ExtractedLink objects (PDFs, images, webpages)

**Key Features:**
- HTML parsing with BeautifulSoup
- Link categorization by type
- Text extraction and cleaning
- Image and PDF link detection

**Dependencies:**
- requests for HTTP requests
- BeautifulSoup4 for HTML parsing

### 4. Content Extractor (app/services/content_extractor.py)

**Purpose:** Extract text content from PDFs and images.

**Input:**
- PDF or image URLs

**Output:**
- Extracted text content

**Key Features:**
- PDF text extraction
- OCR for images using Tesseract
- Error handling for failed extractions

**Dependencies:**
- PyPDF2 for PDF processing
- Pillow (PIL) for image handling
- pytesseract for OCR

### 5. AI Agent (app/services/ai_agent.py)

**Purpose:** Analyze and summarize extracted content using AI.

**Input:**
- Text content
- Context information

**Output:**
- AI-generated summaries and analysis

**Key Features:**
- LangChain integration
- OpenAI GPT-3.5 usage
- Fallback when API key not configured
- Content length management

**Dependencies:**
- langchain for AI orchestration
- langchain-openai for OpenAI integration
- openai for API access

### 6. Application Processor (app/services/processor.py)

**Purpose:** Orchestrate the entire processing pipeline.

**Workflow:**
1. Read entries from Excel file
2. For each entry:
   - Scrape the main website
   - Extract all links
   - Process PDFs (up to 5 per site)
   - Process images with OCR (up to 3 per site)
   - Generate AI summary
3. Return structured data

**Key Features:**
- Sequential processing of applications
- Error handling per application
- Resource limiting (PDF/image counts)
- Progress logging

## Data Flow

```
1. User Request
   ↓
2. FastAPI receives POST /process
   ↓
3. Application Processor initialized
   ↓
4. Excel Reader reads applications.xlsx
   ↓
5. For each application:
   ├─ Web Scraper extracts content and links
   ├─ Content Extractor processes PDFs
   ├─ Content Extractor processes images (OCR)
   └─ AI Agent generates summary
   ↓
6. Structured ApplicationInfo objects created
   ↓
7. JSON response sent to client
```

## Data Models

### WebsiteEntry
```python
{
  "id": int,
  "name": str,
  "url": HttpUrl,
  "description": Optional[str]
}
```

### ExtractedLink
```python
{
  "url": str,
  "link_type": str,  # "webpage", "pdf", "image", "other"
  "title": Optional[str]
}
```

### ExtractedContent
```python
{
  "url": str,
  "content_type": str,  # "webpage", "pdf", "image"
  "text_content": Optional[str],
  "metadata": Dict[str, Any],
  "extracted_at": datetime
}
```

### ApplicationInfo
```python
{
  "id": int,
  "name": str,
  "main_url": str,
  "description": Optional[str],
  "extracted_links": List[ExtractedLink],
  "extracted_contents": List[ExtractedContent],
  "summary": Optional[str],
  "processed_at": datetime
}
```

## Configuration

Configuration is managed through environment variables:

- `OPENAI_API_KEY` - OpenAI API key for AI features
- `APP_HOST` - Server host (default: 0.0.0.0)
- `APP_PORT` - Server port (default: 8000)
- `DEBUG_MODE` - Enable debug mode (default: True)
- `EXCEL_FILE_PATH` - Path to Excel file
- `MAX_CONCURRENT_REQUESTS` - Concurrent request limit
- `REQUEST_TIMEOUT` - HTTP request timeout

## Scalability Considerations

### Current Limitations

1. **Sequential Processing:** Applications processed one at a time
2. **Synchronous Operations:** Blocks during long operations
3. **No Caching:** Repeated requests re-process everything
4. **Memory Usage:** All data held in memory
5. **No Persistence:** Results not stored

### Scaling Strategies

#### Short Term
- Add response caching (Redis)
- Implement request timeouts
- Add rate limiting
- Use connection pooling

#### Medium Term
- Add background task queue (Celery, RQ)
- Implement job status tracking
- Add database for results (PostgreSQL, MongoDB)
- Add progress webhooks/websockets

#### Long Term
- Microservices architecture
- Horizontal scaling with load balancer
- Distributed processing
- Cloud deployment (AWS, GCP, Azure)

## Security Considerations

### Current Implementation
- CORS enabled for all origins (development)
- No authentication/authorization
- No rate limiting
- No input sanitization for uploaded files

### Production Requirements
1. **Authentication:** JWT tokens, API keys, OAuth
2. **CORS:** Restrict to specific frontend origins
3. **Rate Limiting:** Per-IP or per-user limits
4. **Input Validation:** File type, size, content validation
5. **HTTPS:** SSL/TLS encryption
6. **API Key Security:** Secure storage, rotation
7. **Logging & Monitoring:** Security event tracking

## Error Handling

The system implements error handling at multiple levels:

1. **Service Level:** Each service catches and logs errors
2. **Processor Level:** Continues processing on individual failures
3. **API Level:** Returns structured error responses
4. **Global Level:** FastAPI exception handlers

## Monitoring and Logging

Current logging configuration:
- Python logging module
- INFO level in debug mode
- WARNING level in production
- Structured log messages

Recommended additions:
- Structured logging (JSON format)
- Log aggregation (ELK, Splunk)
- Application monitoring (New Relic, DataDog)
- Error tracking (Sentry)

## Deployment Options

### Development
```bash
python -m uvicorn app.main:app --reload
```

### Docker
```bash
docker-compose up
```

### Production
- Use process manager (Gunicorn, Supervisor)
- Set worker count based on CPU cores
- Use reverse proxy (Nginx, Traefik)
- Enable HTTPS
- Configure environment properly

## Performance Characteristics

### Expected Processing Times
- Excel reading: < 1 second
- Website scraping: 2-10 seconds per site
- PDF extraction: 1-5 seconds per PDF
- Image OCR: 2-8 seconds per image
- AI summary: 3-10 seconds per application

### Total per Application
**Typical:** 10-30 seconds per application
**With many PDFs/images:** 1-3 minutes per application

### Optimization Opportunities
1. Parallel processing of applications
2. Concurrent PDF/image processing
3. Caching of previously processed content
4. Batch AI requests
5. Async/await for I/O operations

## Technology Stack

### Core
- **Python 3.8+**
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

### Data Processing
- **pandas** - Excel processing
- **openpyxl** - Excel file handling
- **BeautifulSoup4** - HTML parsing
- **requests** - HTTP client

### Content Extraction
- **PyPDF2** - PDF processing
- **Pillow** - Image handling
- **pytesseract** - OCR

### AI/ML
- **LangChain** - AI orchestration
- **OpenAI** - GPT models
- **langchain-openai** - OpenAI integration

### Development
- **python-dotenv** - Environment management
- **aiofiles** - Async file operations

## Future Enhancements

### Phase 1 (Core Improvements)
- [ ] Add async/await for I/O operations
- [ ] Implement connection pooling
- [ ] Add request/response caching
- [ ] Improve error messages

### Phase 2 (Features)
- [ ] Background job processing
- [ ] Job status API
- [ ] WebSocket progress updates
- [ ] Batch processing API
- [ ] Filtering and search

### Phase 3 (Production Ready)
- [ ] Authentication system
- [ ] Rate limiting
- [ ] Database integration
- [ ] Monitoring dashboard
- [ ] Automated testing

### Phase 4 (Advanced)
- [ ] Multi-language support
- [ ] Custom AI prompts
- [ ] Plugin system
- [ ] API versioning
- [ ] GraphQL API
