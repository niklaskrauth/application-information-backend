@echo off
REM Simple script to run the application on Windows

echo Starting Application Information Backend...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo Warning: Failed to install some dependencies. Please check requirements.txt
    echo Continuing anyway...
)

REM Check for .env file
if not exist ".env" (
    echo Warning: .env file not found. Copying from .env.example...
    copy .env.example .env >nul
    echo Please edit .env file and configure your Ollama settings!
)

REM Create sample Excel if it doesn't exist
if not exist "data\Landratsamt.xlsx" (
    echo Creating sample Excel file...
    python create_sample_excel.py
)

REM Run the application
echo.
echo Starting server at http://localhost:8000
echo API documentation available at http://localhost:8000/docs
echo.
python -m uvicorn app.main:app --reload
