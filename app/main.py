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
    # For Ollama, we assume it's configured if the provider is set
    # The actual connection check happens when AIAgent is initialized
    ai_configured = True
    
    return {
        "status": "healthy",
        "ai_provider": "ollama",
        "ai_configured": ai_configured
    }


@app.get("/jobs", response_model=Table)
async def get_jobs():
    """
    Process all company entries from Excel and extract job information.
    
    This endpoint processes entries sequentially:
    - Scrapes each website
    - Sends to AI for analysis
    - Adds to response
    - Then moves to the next website
    
    This approach is more efficient than processing all links at once.
    
    Returns:
        Table with rows containing job information for each company
    """
    try:
        # Check if Excel file exists
        logger.info(f"Checking if file exists: {settings.EXCEL_FILE_PATH}")
        if not os.path.exists(settings.EXCEL_FILE_PATH):
            logger.error(f"Excel file not found: {settings.EXCEL_FILE_PATH}")
            raise HTTPException(
                status_code=404,
                detail=f"Excel file not found at {settings.EXCEL_FILE_PATH}"
            )

        # Create JobProcessor and start processing
        logger.info("Creating JobProcessor and starting processing...")

        # Create processor and process jobs incrementally
        processor = JobProcessor(
            excel_path=settings.EXCEL_FILE_PATH,
            timeout=settings.REQUEST_TIMEOUT
        )
        
        # Collect all rows from incremental processing
        rows = []
        for row in processor.process_jobs_incrementally():
            rows.append(row)
        
        table = Table(rows=rows)
        
        logger.info(f"Successfully processed {len(table.rows)} job entries")
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
