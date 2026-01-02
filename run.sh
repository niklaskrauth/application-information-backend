#!/bin/bash
# Simple script to run the application

echo "Starting Application Information Backend..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
if ! source venv/bin/activate; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
if ! pip install -r requirements.txt > /dev/null; then
    echo "Warning: Failed to install some dependencies. Please check requirements.txt"
    echo "Continuing anyway..."
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "Please edit .env file and configure your Hugging Face settings if needed!"
fi

# Create sample Excel if it doesn't exist
if [ ! -f "data/Landratsamt.xlsx" ]; then
    echo "Creating sample Excel file..."
    python create_sample_excel.py
fi

# Run the application
echo ""
echo "Starting server at http://localhost:8000"
echo "API documentation available at http://localhost:8000/docs"
echo ""
python -m uvicorn app.main:app --reload
