# Application Information Backend

A Python backend using LangChain and Groq AI for extracting job information from company websites. The system reads company locations from an Excel sheet, scrapes their job pages, and uses AI to extract structured job information for frontend consumption.

## Features

- **Excel Integration**: Read company data from Excel sheets
- **Web Scraping**: Automatically scrape company job pages
- **AI Job Extraction**: Use LangChain and Groq (LLaMA 3.1 70B) to analyze and extract job details
- **REST API**: FastAPI-based REST API with single GET endpoint
- **Structured JSON Output**: Returns job data matching frontend TypeScript interfaces

## Architecture

```
Excel File (src/data/excel.xls) → Excel Reader → Website Scraper → Groq AI Agent → Table JSON Response
```

## Requirements

- Python 3.8+
- Groq API Key (for AI-powered job extraction)

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

Edit `.env` and add your Groq API key:
```
GROQ_API_KEY=your_actual_groq_api_key_here
```

You can get a free Groq API key at: https://console.groq.com/

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
docker run -p 8000:8000 -v $(pwd)/src/data:/app/src/data -e GROQ_API_KEY=your_key application-info-backend
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
- Uses Groq AI to analyze and extract job details
- **Extracts ALL jobs found on each company's page** (multiple jobs per company)
- Returns structured job data matching the frontend interface
- **Implements rate limiting** to avoid API throttling

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

Check if the API is running and Groq is configured.

**Response:**
```json
{
  "status": "healthy",
  "groq_configured": true
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
│   │   ├── ai_agent.py         # Groq AI agent for job extraction
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
3. **AI Analysis**: `AIAgent` uses LangChain and Groq (LLaMA 3.1 70B) to:
   - Analyze job page content
   - Extract structured job information for **ALL jobs found** (title, salary, home office, etc.)
   - Determine if positions are available
   - Apply rate limiting between API calls to avoid throttling
4. **JSON Response**: All data is structured into a Table with TableRow objects matching the frontend interface
   - **Multiple jobs per company**: If a company has 3 jobs, 3 separate TableRow entries are returned

## Configuration

All configuration is managed through environment variables (`.env` file):

```bash
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG_MODE=True

# Excel File Path
EXCEL_FILE_PATH=src/data/excel.xls

# Processing Configuration
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT=30

# AI Rate Limiting (seconds between API calls)
AI_RATE_LIMIT_DELAY=2
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

- **Rate Limiting**: Be mindful of rate limits when scraping websites
- **Processing Time**: Each company entry requires scraping and AI analysis (typically 5-15 seconds per company)
- **API Costs**: Groq API has generous free tier, but usage is rate-limited
- **Content Accuracy**: AI extraction depends on the structure and clarity of the job page content

## Troubleshooting

### Common Issues

1. **"Groq API key not set"**
   - Ensure you've set `GROQ_API_KEY` in your `.env` file
   - Get a free API key at https://console.groq.com/
   - Restart the server after updating `.env`

2. **"Excel file not found"**
   - Run `python create_sample_excel.py` to create the sample file
   - Ensure the file is at `src/data/excel.xls`
   - Check the path in `.env` is correct

3. **Import errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Activate your virtual environment

4. **Slow processing**
   - Consider reducing the number of companies in the Excel file
   - Check your internet connection
   - Groq API rate limits may cause delays

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.