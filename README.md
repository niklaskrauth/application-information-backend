# Application Information Backend

A Python backend using LangChain with Ollama for extracting job information from company websites. The system reads company locations from an Excel sheet, scrapes their job pages, and uses AI to extract structured job information for frontend consumption.

**Uses Ollama to run AI models locally - no API keys needed, no rate limits!**

## Features

- **Excel Integration**: Read company data from Excel sheets
- **Web Scraping**: Automatically scrape company job pages
- **AI Job Extraction**: Use LangChain with Ollama (LLaMA 3.1/3.2 or other models) - Run AI locally, no API keys needed, no rate limits
- **REST API**: FastAPI-based REST API with single GET endpoint
- **Structured JSON Output**: Returns job data matching frontend TypeScript interfaces

## Architecture

```
Excel File (src/data/excel.xls) → Excel Reader → Website Scraper → AI Agent (Ollama) → Table JSON Response
```

## Requirements

- Python 3.8+
- Ollama installed and running (for local AI-powered job extraction, no API key needed)

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

**Configure Ollama settings:**

**Step 1: Install Ollama**

Visit https://ollama.ai and download Ollama for your operating system:
- **macOS**: Download the .dmg file and install
- **Linux**: Run `curl -fsSL https://ollama.ai/install.sh | sh`
- **Windows**: Download the installer from the website

**Step 2: Start Ollama and pull a model**

```bash
# Start Ollama (if not already running)
ollama serve

# In a new terminal, pull the recommended model (8B parameter version)
ollama pull llama3.1:8b

# Or for better quality (requires more RAM/VRAM):
ollama pull llama3.1:70b
```

**Step 3: Configure the application**

Edit `.env` and configure Ollama:
```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

**Available Ollama models:**
- `llama3.1:8b` - Recommended, good balance of speed and quality (8GB RAM required)
- `llama3.1:70b` - Best quality, slower (40GB RAM required)
- `llama3.2:8b` - Latest version, similar to 3.1
- `mistral:7b` - Alternative, good performance
- See more at: https://ollama.ai/library

### 5. Create sample Excel file

```bash
python create_sample_excel.py
```

This creates a sample `src/data/excel.xls` file with example company data.

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

The Excel file should be located at `src/data/excel.xls` and have the following columns:

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

Run the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

Or:

```bash
cd app
python main.py
```

The server will start at `http://localhost:8000`

### API Endpoint

#### GET /jobs

Process all companies from the Excel file and extract job information.

This endpoint:
- Reads all company entries from `src/data/excel.xls`
- Scrapes each company's jobs page (websiteToJobs or website)
- Uses Ollama AI to analyze and extract job details
- **Extracts ALL jobs found on each company's page** (multiple jobs per company)
- Returns structured job data matching the frontend interface

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
    foundOn?: string;
    comments?: string;
}
```

**Example Request:**
```bash
curl http://localhost:8000/jobs
```

**Example with JavaScript:**
```javascript
fetch('http://localhost:8000/jobs')
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.rows.length} companies`);
    data.rows.forEach(row => {
      console.log(`${row.location}: ${row.hasJob ? 'Has jobs!' : 'No jobs'}`);
    });
  });
```

#### GET /health

Check if the API is running and AI provider is configured.

**Response:**
```json
{
  "status": "healthy",
  "ai_provider": "ollama",
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
│   │   ├── ai_agent.py         # AI agent for job extraction (Ollama)
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

1. **Excel Reading**: The system reads company entries from `src/data/excel.xls` using `ExcelReader`
2. **Web Scraping**: For each entry, `WebScraper` visits the jobs page (websiteToJobs or website) and extracts text content
3. **AI Analysis**: `AIAgent` uses LangChain with Ollama to:
   - Analyze job page content
   - Extract structured job information for **ALL jobs found** (title, salary, home office, etc.)
   - Determine if positions are available
4. **JSON Response**: All data is structured into a Table with TableRow objects matching the frontend interface
   - **Multiple jobs per company**: If a company has 3 jobs, 3 separate TableRow entries are returned

## Configuration

All configuration is managed through environment variables (`.env` file):

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG_MODE=True

# Excel File Path
EXCEL_FILE_PATH=data/Landratsamt.xlsx

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
  - **Ollama**: No rate limits, processing speed depends on your hardware
  - **Web Scraping**: Be respectful of rate limits when scraping websites
- **Processing Time**: 
  - Each company entry requires scraping and AI analysis
  - **Ollama**: Varies by hardware (8B model: 10-30 seconds, 70B model: 30-120 seconds per company)
- **API Costs**: 
  - **Ollama**: Completely free, runs locally, no API costs
- **Hardware Requirements (Ollama)**:
  - 8B models: 8GB RAM minimum, 16GB recommended
  - 70B models: 40GB RAM minimum, GPU recommended for better performance
- **Content Accuracy**: AI extraction depends on the structure and clarity of the job page content

## Troubleshooting

### Common Issues

1. **"Failed to initialize Ollama"**
   - Make sure Ollama is installed and running: `ollama serve`
   - Verify the model is downloaded: `ollama list`
   - If not downloaded, pull it: `ollama pull llama3.1:8b`
   - Check that OLLAMA_BASE_URL in `.env` matches where Ollama is running
   - Default is `http://localhost:11434`

2. **"Ollama provider requires langchain-ollama"**
   - Install the Ollama dependency: `pip install langchain-ollama`
   - Or reinstall all dependencies: `pip install -r requirements.txt`

3. **"Excel file not found"**
   - Run `python create_sample_excel.py` to create the sample file
   - Ensure the file is at `src/data/excel.xls`
   - Check the path in `.env` is correct

4. **Import errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Activate your virtual environment

5. **Slow processing**
   - **For Ollama**: 
     - Use a smaller model (e.g., `llama3.1:8b` instead of `llama3.1:70b`)
     - Ensure adequate RAM/VRAM available
     - Consider using GPU acceleration if available
   - Consider reducing the number of companies in the Excel file for testing

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.