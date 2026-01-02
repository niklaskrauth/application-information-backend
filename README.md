# Application Information Backend

A Python backend using LangChain with Hugging Face for extracting job information from company websites. The system reads company locations from an Excel sheet, scrapes their job pages, and uses AI to extract structured job information. Results are saved as JSON files that can be uploaded to your website.

**Uses powerful German language models from Hugging Face - optimized for German text processing, no API keys needed!**

## Features

- **Excel Integration**: Read company data from Excel sheets
- **Web Scraping**: Automatically scrape company job pages
- **AI Job Extraction**: Use LangChain with Hugging Face (German-optimized models) - Local AI processing, no API keys needed, no rate limits
- **REST API**: FastAPI-based REST API for job processing and export management
- **JSON File Export**: Saves structured job data as JSON files ready for website upload

## Architecture

```
Excel File (data/Landratsamt.xlsx) → Excel Reader → Website Scraper → AI Agent (Hugging Face) → JSON File Export (data/output/)
```

## Requirements

- Python 3.8+
- At least 8GB RAM (16GB recommended for optimal performance)
- Internet connection for initial model download (models are cached locally after first download)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/niklaskrauth/application-information-backend.git
cd application-information-backend
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example environment file and update with your settings:

```bash
cp .env.example .env
```

**Configure Hugging Face settings:**

The application uses powerful German language models from Hugging Face. The default configuration uses:

```
HUGGINGFACE_MODEL=Veronika-T/mistral-german-7b
HUGGINGFACE_EMBEDDING_MODEL=deutsche-telekom/gbert-large-paraphrase-cosine
HUGGINGFACE_API_TOKEN=
```

**About the German models:**

1. **Veronika-T/mistral-german-7b**: A powerful German-optimized text generation model specifically trained for German language understanding and generation. Perfect for analyzing German job postings.

2. **deutsche-telekom/gbert-large-paraphrase-cosine**: A German BERT model optimized for semantic similarity and embeddings, ideal for understanding context in German text.

**Initial Setup:**

**Important:** Models are now downloaded automatically when the application starts, not when the first request is made. On the first startup, the application will download models from Hugging Face (approximately 15-20GB total) and cache them locally in `~/.cache/huggingface/`. Subsequent startups will use the cached models and start much faster.

The startup process will:
1. Download the text generation model if not cached (first run only)
2. Download the embedding model if not cached (first run only)
3. Load both models into memory
4. Make them ready for immediate use when requests arrive

This ensures fast response times for all requests after startup.

**Optional: Hugging Face API Token**

Most models don't require an API token, but if you want to use gated models:

1. Create a free account at https://huggingface.co
2. Get your token from https://huggingface.co/settings/tokens
3. Add it to `.env`:
   ```
   HUGGINGFACE_API_TOKEN=hf_your_token_here
   ```

**Alternative German Models:**

You can configure different German models by editing `.env`:

- **Text Generation Models**:
  - `Veronika-T/mistral-german-7b` (default, recommended)
  - `LeoLM/leo-hessianai-7b` (alternative German model)
  - `VAGOsolutions/SauerkrautLM-7b-HerO` (another German-optimized model)

- **Embedding Models**:
  - `deutsche-telekom/gbert-large-paraphrase-cosine` (default, recommended)
  - `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` (multilingual fallback)
  - `T-Systems-onsite/german-roberta-sentence-transformer-v2` (alternative German embeddings)

### 5. Create sample Excel file

```bash
python create_sample_excel.py
```

This creates a sample `data/Landratsamt.xlsx` file with example company data.

### Alternative: Using Docker

If you prefer using Docker:

```bash
# Build and run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

Or build manually:

```bash
# Build the image
docker build -t application-info-backend .

# Run the container
docker run -p 8000:8000 -v $(pwd)/src/data:/app/src/data application-info-backend
```

## Excel File Format

The Excel file should be located at `data/Landratsamt.xlsx` and have the following columns:

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| id | Integer | Yes | Unique identifier for the company |
| location | String | Yes | Company location (e.g., "Berlin, Germany") |
| website | String | Yes | Main company website URL |
| websiteToJobs | String | No | Direct URL to jobs/careers page (if different from main website) |

Example:
```
id  | location         | website                        | websiteToJobs
----|------------------|--------------------------------|----------------------------------
1   | Berlin, Germany  | https://www.example.com        | https://www.example.com/careers
2   | Munich, Germany  | https://www.another.com        | https://www.another.com/jobs
```

## Usage

### Starting the Server

**Important:** On first startup, the server will download AI models (~15-20GB). This can take 10-30 minutes depending on your internet connection. Subsequent startups are much faster as models are cached locally.

Run the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

Watch the startup logs to monitor model download progress:
- "Downloading model if not cached locally..." - Model download in progress
- "Model downloaded and cached successfully" - Text generation model ready
- "Embedding model downloaded and cached successfully" - Embedding model ready
- "Models are now cached locally and available for offline use" - Startup complete

Or use the convenience scripts:

**On Linux/Mac:**
```bash
./run.sh
```

**On Windows:**
```bash
.\run.bat
```

Or manually:

```bash
cd app
python main.py
```

The server will start at `http://localhost:8000`

### API Endpoints

#### GET /jobs

Process all companies from the Excel file and extract job information.

This endpoint:
- Reads all company entries from `data/Landratsamt.xlsx`
- Scrapes each company's jobs page (websiteToJobs or website)
- Uses Hugging Face AI models to analyze and extract job details
- **Extracts ALL jobs found on each company's page** (multiple jobs per company)
- **Saves results to a JSON file** in the output directory (default: `data/output/`)
- Returns immediately with processing status

The endpoint starts processing in the background and returns a status response. When processing completes, a timestamped JSON file is created (e.g., `jobs_export_20260102_143000.json`) that can be uploaded to your website.

**Response Format:**
```json
{
  "status": "processing",
  "message": "Job processing started. Results will be saved to a JSON file when complete.",
  "output_directory": "data/output"
}
```

**Example Request:**
```bash
curl http://localhost:8000/jobs
```

#### GET /exports

List all generated JSON export files.

This endpoint returns a list of all JSON files that have been generated from job processing, including metadata like file size and creation time.

**Response Format:**
```json
{
  "exports": [
    {
      "filename": "jobs_export_20260102_143000.json",
      "path": "data/output/jobs_export_20260102_143000.json",
      "size_bytes": 12345,
      "created_at": "2026-01-02T14:30:00"
    }
  ],
  "count": 1,
  "output_directory": "data/output"
}
```

**Example Request:**
```bash
curl http://localhost:8000/exports
```

#### JSON Export File Format

The generated JSON files contain structured job data matching the frontend interface:

**Note:** If a company has multiple job openings, each job will be returned as a separate row in the response with the same `location`, `website`, and `websiteToJobs` fields.

**Response Format:**
```json
{
  "rows": [
    {
      "location": "Berlin, Germany",
      "website": "https://www.example-company.com",
      "websiteToJobs": "https://www.example-company.com/careers",
      "hasJob": true,
      "name": "Senior Software Engineer",
      "salary": "€70,000 - €90,000",
      "homeOfficeOption": true,
      "period": "Full-time",
      "employmentType": "Permanent",
      "applicationDate": null,
      "occupyStart": "2025-01-15",
      "foundOn": "Main page",
      "comments": "Remote work available, flexible hours"
    },
    {
      "location": "Berlin, Germany",
      "website": "https://www.example-company.com",
      "websiteToJobs": "https://www.example-company.com/careers",
      "hasJob": true,
      "name": "Junior Developer",
      "salary": "€45,000 - €55,000",
      "homeOfficeOption": true,
      "period": "Full-time",
      "employmentType": "Permanent",
      "applicationDate": null,
      "occupyStart": null,
      "foundOn": "PDF: career_opportunities.pdf",
      "comments": "Great for entry-level candidates"
    },
    {
      "location": "Munich, Germany",
      "website": "https://www.another-company.com",
      "websiteToJobs": "https://www.another-company.com/jobs",
      "hasJob": false,
      "name": null,
      "salary": null,
      "homeOfficeOption": null,
      "period": null,
      "employmentType": null,
      "applicationDate": null,
      "occupyStart": null,
      "foundOn": null,
      "comments": "No open positions at this time"
    }
  ]
}
```

**TypeScript Interface:**
```typescript
interface Table {
    rows: TableRow[];
}

interface TableRow {
    location: string;
    website: string;
    websiteToJobs: string;
    hasJob: boolean;
    name?: string;
    salary?: string;
    homeOfficeOption?: boolean;
    period?: string;
    employmentType?: string;
    applicationDate?: Date;
    occupyStart?: Date;
    foundOn?: string;
    comments?: string;
}
```

**Using the JSON Files:**

After the `/jobs` endpoint completes processing (which runs in the background), you can:

1. List available exports using the `/exports` endpoint
2. Locate the JSON file in the `data/output/` directory
3. Upload the JSON file to your website
4. Parse and use the structured job data in your frontend application

**Example Workflow:**
```bash
# Start job processing
curl http://localhost:8000/jobs

# Wait for processing to complete (monitor logs)

# List available exports
curl http://localhost:8000/exports

# The JSON file will be at data/output/jobs_export_YYYYMMDD_HHMMSS.json
```

#### GET /health

Check if the API is running and AI provider is configured.

**Response:**
```json
{
  "status": "healthy",
  "ai_provider": "huggingface",
  "ai_configured": true
}
```

### Interactive API Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
application-information-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration and settings
│   ├── models/
│   │   └── __init__.py         # Pydantic models (Table, TableRow)
│   ├── services/
│   │   ├── excel_reader.py     # Excel file reading service
│   │   ├── web_scraper.py      # Website scraping service
│   │   ├── ai_agent.py         # AI agent for job extraction (Hugging Face)
│   │   └── processor.py        # Job processing orchestration
│   └── utils/
├── src/
│   └── data/
│       └── excel.xls           # Excel file with company data
├── .env                        # Environment variables (not in git)
├── .env.example                # Example environment file
├── .gitignore                  # Git ignore file
├── requirements.txt            # Python dependencies
├── create_sample_excel.py      # Script to create sample Excel
└── README.md                   # This file
```

## How It Works

1. **Excel Reading**: The system reads company entries from `data/Landratsamt.xlsx` using `ExcelReader`
2. **Web Scraping**: For each entry, `WebScraper` visits the jobs page (websiteToJobs or website) and extracts text content
3. **AI Analysis**: `AIAgent` uses LangChain with Hugging Face to:
   - Analyze job page content
   - Extract structured job information for **ALL jobs found** (title, salary, home office, etc.)
   - Determine if positions are available
4. **JSON Export**: All data is structured into a Table with TableRow objects and saved as a JSON file
   - **Multiple jobs per company**: If a company has 3 jobs, 3 separate TableRow entries are created
   - **Timestamped files**: Each export is saved with a unique timestamp (e.g., `jobs_export_20260102_143000.json`)
   - **Ready for upload**: The generated JSON file can be uploaded directly to your website

## Configuration

All configuration is managed through environment variables (`.env` file):

```bash
# Hugging Face Configuration
HUGGINGFACE_MODEL=Veronika-T/mistral-german-7b
HUGGINGFACE_EMBEDDING_MODEL=deutsche-telekom/gbert-large-paraphrase-cosine
HUGGINGFACE_API_TOKEN=

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG_MODE=True

# Excel File Path
EXCEL_FILE_PATH=data/Landratsamt.xlsx

# JSON Output Directory
JSON_OUTPUT_DIR=data/output

# Processing Configuration
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT=30
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Style

```bash
# Install formatting tools
pip install black isort flake8

# Format code
black app/
isort app/

# Lint code
flake8 app/
```

## Limitations and Considerations

- **Rate Limiting**: 
  - **Hugging Face**: No rate limits, all processing is local
  - **Web Scraping**: Be respectful of rate limits when scraping websites
- **Processing Time**: 
  - Each company entry requires scraping and AI analysis
  - **Hugging Face**: 
    - First startup downloads models (~15-20GB, one-time, 10-30 minutes)
    - Subsequent startups are fast (1-2 minutes to load cached models)
    - Processing: 10-60 seconds per company depending on hardware
- **API Costs**: 
  - **Hugging Face**: Completely free, all processing is local, no API costs
- **Hardware Requirements**:
  - 8GB RAM minimum for basic operation
  - 16GB RAM recommended for optimal performance
  - GPU optional but recommended for faster inference
  - ~20GB disk space for model storage
- **Content Accuracy**: AI extraction depends on the structure and clarity of the job page content

## Troubleshooting

### Common Issues

1. **"Failed to initialize Hugging Face" or slow startup**
   - **First startup is slow**: Models are downloaded on first startup (~15-20GB, 10-30 minutes)
   - Ensure you have at least 8GB RAM available (16GB recommended)
   - Check internet connection for initial model download (required only on first startup)
   - Models are downloaded to `~/.cache/huggingface/` - ensure enough disk space (~20GB)
   - For GPU acceleration, ensure PyTorch with CUDA support is installed
   - Check error logs for specific model loading issues
   - **Subsequent startups are fast** (1-2 minutes) as models are cached locally

2. **"Hugging Face provider requires langchain-huggingface"**
   - Install the Hugging Face dependencies: `pip install langchain-huggingface transformers sentence-transformers`
   - Or reinstall all dependencies: `pip install -r requirements.txt`

3. **"Excel file not found"**
   - Run `python create_sample_excel.py` to create the sample file
   - Ensure the file is at `data/Landratsamt.xlsx`
   - Check the path in `.env` is correct

4. **Import errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Activate your virtual environment

5. **Slow processing**
   - **For Hugging Face**: 
     - First startup downloads models (~15-20GB, 10-30 minutes) - this is normal
     - Subsequent startups are fast (1-2 minutes) using cached models
     - Ensure adequate RAM available (16GB recommended)
     - Consider using GPU acceleration by installing PyTorch with CUDA: `pip install torch --index-url https://download.pytorch.org/whl/cu118`
     - You can use smaller/faster models by changing HUGGINGFACE_MODEL in `.env`
   - Consider reducing the number of companies in the Excel file for testing

6. **Model download issues**
   - If model download fails during startup, check your internet connection
   - Ensure `~/.cache/huggingface/` directory has write permissions
   - Try clearing the cache: `rm -rf ~/.cache/huggingface/` and restart the application
   - For gated models, ensure HUGGINGFACE_API_TOKEN is set correctly
   - Check startup logs for detailed error messages

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.