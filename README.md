# Application Information Backend

A Python backend using LangChain AI/agent for extracting information from website applications. The system reads website URLs from an Excel sheet, scrapes the websites, extracts content from linked PDFs and images, and provides structured JSON data for frontend consumption.

## Features

- **Excel Integration**: Read website application data from Excel sheets
- **Web Scraping**: Automatically scrape websites and extract links
- **PDF Processing**: Extract text content from PDF documents
- **Image OCR**: Extract text from images using OCR (Optical Character Recognition)
- **AI Analysis**: Use LangChain and OpenAI to analyze and summarize extracted content
- **REST API**: FastAPI-based REST API for frontend integration
- **JSON Output**: Structured JSON responses for easy frontend consumption

## Architecture

```
Excel File → Excel Reader → Website Scraper → Content Extractors (PDF/Image) → AI Agent → JSON Response
```

## Requirements

- Python 3.8+
- OpenAI API Key (for AI-powered analysis)
- Tesseract OCR (for image text extraction)

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

### 4. Install Tesseract OCR (for image text extraction)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

### 5. Configure environment variables

Copy the example environment file and update with your settings:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 6. Create sample Excel file

```bash
python create_sample_excel.py
```

This creates a sample `data/applications.xlsx` file with example data.

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
docker run -p 8000:8000 -v $(pwd)/data:/app/data -e OPENAI_API_KEY=your_key application-info-backend
```

## Excel File Format

The Excel file should have the following columns:

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| id | Integer | Yes | Unique identifier for the application |
| name | String | Yes | Name of the application/website |
| url | String | Yes | Full URL of the website (must include http:// or https://) |
| description | String | No | Optional description of the application |

Example:
```
id  | name            | url                        | description
----|-----------------|----------------------------|---------------------------
1   | Example Company | https://www.example.com    | A sample company website
2   | Tech Startup    | https://www.github.com     | Open source platform
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

### API Endpoints

#### 1. Health Check
```bash
GET /health
```

Check if the API is running and OpenAI is configured.

**Response:**
```json
{
  "status": "healthy",
  "openai_configured": true
}
```

#### 2. Get Applications List
```bash
GET /applications
```

Retrieve the list of applications from the Excel file without processing.

**Response:**
```json
{
  "success": true,
  "count": 3,
  "applications": [
    {
      "id": 1,
      "name": "Example Company",
      "url": "https://www.example.com",
      "description": "A sample company website"
    }
  ]
}
```

#### 3. Process Applications
```bash
POST /process
```

Process all applications from the Excel file. This endpoint:
- Reads all entries from the Excel file
- Scrapes each website
- Extracts content from PDFs and images
- Uses AI to analyze and summarize the information
- Returns structured JSON data

**Response:**
```json
{
  "success": true,
  "message": "Successfully processed 3 applications",
  "data": [
    {
      "id": 1,
      "name": "Example Company",
      "main_url": "https://www.example.com",
      "description": "A sample company website",
      "extracted_links": [
        {
          "url": "https://www.example.com/about",
          "link_type": "webpage",
          "title": "About Us"
        },
        {
          "url": "https://www.example.com/brochure.pdf",
          "link_type": "pdf",
          "title": "Company Brochure"
        }
      ],
      "extracted_contents": [
        {
          "url": "https://www.example.com",
          "content_type": "webpage",
          "text_content": "...",
          "metadata": {"is_main_page": true},
          "extracted_at": "2025-11-01T11:37:13.317Z"
        }
      ],
      "summary": "AI-generated summary of the application...",
      "processed_at": "2025-11-01T11:37:13.317Z"
    }
  ]
}
```

#### 4. Upload Excel File
```bash
POST /upload-excel
Content-Type: multipart/form-data

file: <excel_file>
```

Upload a new Excel file with website applications.

**Response:**
```json
{
  "success": true,
  "message": "Excel file uploaded successfully",
  "file_path": "data/applications.xlsx"
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
│   │   └── __init__.py         # Pydantic models for data structures
│   ├── services/
│   │   ├── excel_reader.py     # Excel file reading service
│   │   ├── web_scraper.py      # Website scraping service
│   │   ├── content_extractor.py # PDF and image content extraction
│   │   ├── ai_agent.py         # LangChain AI agent for analysis
│   │   └── processor.py        # Main orchestration service
│   └── utils/
├── data/
│   └── applications.xlsx       # Excel file with website data
├── .env                        # Environment variables (not in git)
├── .env.example                # Example environment file
├── .gitignore                  # Git ignore file
├── requirements.txt            # Python dependencies
├── create_sample_excel.py      # Script to create sample Excel
└── README.md                   # This file
```

## How It Works

1. **Excel Reading**: The system reads website entries from an Excel file using `ExcelReader`
2. **Web Scraping**: For each entry, `WebScraper` visits the website and extracts:
   - Main page text content
   - All links (webpages, PDFs, images)
3. **Content Extraction**: 
   - `ContentExtractor` processes PDFs to extract text
   - OCR is used to extract text from images
4. **AI Analysis**: `AIAgent` uses LangChain and OpenAI to:
   - Summarize extracted content
   - Provide insights about the application
   - Generate comprehensive analysis
5. **JSON Response**: All data is structured into JSON format for frontend consumption

## Configuration

All configuration is managed through environment variables (`.env` file):

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG_MODE=True

# Excel File Path
EXCEL_FILE_PATH=data/applications.xlsx

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

- **Rate Limiting**: Be mindful of rate limits when scraping websites
- **PDF/Image Processing**: Limited to first 5 PDFs and 3 images per website to manage processing time
- **Content Length**: AI summaries are limited to the first 5000 characters of content
- **OCR Accuracy**: Image text extraction depends on image quality and Tesseract configuration
- **API Costs**: OpenAI API usage incurs costs based on token usage

## Troubleshooting

### Common Issues

1. **"OpenAI API key not set"**
   - Ensure you've set `OPENAI_API_KEY` in your `.env` file
   - Restart the server after updating `.env`

2. **"Excel file not found"**
   - Run `python create_sample_excel.py` to create the sample file
   - Ensure the path in `.env` is correct

3. **Tesseract not found**
   - Install Tesseract OCR for your system
   - Ensure it's in your system PATH

4. **Import errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Activate your virtual environment

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.