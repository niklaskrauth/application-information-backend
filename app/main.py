from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from app.config import settings
from app.models import Table
from app.services.processor import JobProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG_MODE else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Application Information Backend",
    description="Backend API for extracting job information from company websites using AI",
    version="2.0.0"
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Application Information Backend API",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "groq_configured": bool(settings.GROQ_API_KEY)
    }


@app.get("/jobs", response_model=Table)
async def get_jobs():
    """
    Process all company entries from Excel and extract job information.
    
    This endpoint:
    - Reads company entries from the Excel file (src/data/excel.xls)
    - Scrapes each company's jobs page
    - Uses AI to analyze and extract job details
    - Returns structured job information matching the frontend Table interface
    
    Returns:
        Table with rows containing job information for each company
    """
    import time
    start_time = time.time()
    
    try:
        # Check if Excel file exists
        logger.info(f"Überprüfe, ob die Datei existiert: {settings.EXCEL_FILE_PATH}")
        if not os.path.exists(settings.EXCEL_FILE_PATH):
            logger.error(f"Excel-Datei nicht gefunden: {settings.EXCEL_FILE_PATH}")
            raise HTTPException(
                status_code=404,
                detail=f"Excel-Datei nicht gefunden unter {settings.EXCEL_FILE_PATH}"
            )

        # JobProcessor erstellen und Jobs verarbeiten
        logger.info("Erstelle JobProcessor und starte Verarbeitung...")


        # Create processor and process jobs
        processor = JobProcessor(
            excel_path=settings.EXCEL_FILE_PATH,
            timeout=settings.REQUEST_TIMEOUT
        )
        
        table = processor.process_all_jobs()
        
        elapsed_time = time.time() - start_time
        logger.info(f"Successfully processed {len(table.rows)} job entries in {elapsed_time:.2f} seconds")
        return table
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error processing jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG_MODE
    )
