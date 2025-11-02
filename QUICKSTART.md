# Quick Start Guide

Get up and running with the Application Information Backend in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- Ollama (local AI, no API key needed, no rate limits)

## Step 1: Clone and Install

```bash
# Clone the repository
git clone https://github.com/niklaskrauth/application-information-backend.git
cd application-information-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Ollama

```bash
# 1. Install Ollama
# Visit https://ollama.ai and follow installation instructions for your OS
# macOS/Linux: curl -fsSL https://ollama.ai/install.sh | sh

# 2. Start Ollama and pull a model
ollama serve  # Start Ollama server
# In a new terminal:
ollama pull llama3.1:8b  # Download recommended model (8GB RAM required)

# 3. Configure the application
cp .env.example .env
nano .env
```

Set in `.env`:
```
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
AI_RATE_LIMIT_DELAY=0
```

**Note:** Also install the langchain-ollama package:
```bash
pip install langchain-ollama
```

## Step 3: Create Sample Data

```bash
# Generate sample Excel file
python create_sample_excel.py
```

## Step 4: Start the Server

```bash
# Run the server
python -m uvicorn app.main:app --reload
```

Or use the convenience script:
```bash
./run.sh
```

## Step 5: Test the API

Open your browser and visit:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

Or use the example script:
```bash
python example_usage.py
```

## Step 6: Process Applications

### Via API Documentation (Browser)

1. Go to http://localhost:8000/docs
2. Click on `POST /process`
3. Click "Try it out"
4. Click "Execute"
5. View the JSON response

### Via Command Line

```bash
curl -X POST http://localhost:8000/process
```

### Via Python Script

```bash
python example_usage.py
```

## What's Next?

### Customize Your Excel File

Edit `data/applications.xlsx` with your own website URLs:

| id | name | url | description |
|----|------|-----|-------------|
| 1 | My Website | https://example.com | My description |

### Integrate with Frontend

Use the JSON responses in your frontend application:

```javascript
// Fetch applications
fetch('http://localhost:8000/applications')
  .then(response => response.json())
  .then(data => console.log(data));

// Process applications
fetch('http://localhost:8000/process', {method: 'POST'})
  .then(response => response.json())
  .then(data => console.log(data));
```

### Explore API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /applications` - List applications from Excel
- `POST /process` - Process all applications
- `POST /upload-excel` - Upload new Excel file

## Troubleshooting

### Server won't start

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Ollama errors

```bash
# Make sure Ollama is running
ollama serve

# Verify model is downloaded
ollama list

# If model is missing, download it
ollama pull llama3.1:8b

# Install langchain-ollama package
pip install langchain-ollama
```

### Excel file not found

```bash
python create_sample_excel.py
```

### Import errors

```bash
# Validate your setup
python validate.py
```

## Need Help?

- Check the full [README.md](README.md)
- Review [API Documentation](http://localhost:8000/docs)
- Open an issue on GitHub

Happy coding! 🚀
