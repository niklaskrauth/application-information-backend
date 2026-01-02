from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional
import logging
import os
import httpx
from app.config import settings
from app.models import Table
from app.services.processor import JobProcessor
from app.services.ai_agent import AIAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG_MODE else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Global AI agent instance (initialized on startup)
ai_agent: Optional[AIAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    
    This ensures that:
    - Models are downloaded if not already cached
    - Models are loaded into memory and ready to use
    - First request doesn't have to wait for model download/loading
    """
    global ai_agent
    logger.info("Starting application initialization...")
    logger.info("Downloading and loading AI models (this may take a while on first run)...")
    
    try:
        ai_agent = AIAgent()
        if ai_agent.enabled:
            logger.info("AI models successfully loaded and ready!")
        else:
            logger.warning("AI agent is disabled. Check logs for details.")
    except Exception as e:
        logger.error(f"Failed to initialize AI agent: {str(e)}")
        logger.error("Application will continue but AI features will be unavailable")
        ai_agent = None
    
    logger.info("Application startup complete")
    
    yield
    
    # Cleanup (if needed)
    logger.info("Application shutting down...")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Application Information Backend",
    description="Backend API for extracting job information from company websites using AI",
    version="2.0.0",
    lifespan=lifespan
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
    # For Hugging Face, we assume it's configured if the provider is set
    # The actual connection check happens when AIAgent is initialized
    ai_configured = True
    
    return {
        "status": "healthy",
        "ai_provider": "huggingface",
        "ai_configured": ai_configured
    }


async def _process_jobs() -> Table:
    """
    Internal function to process all jobs.
    
    Returns:
        Table with rows containing job information for each company
    
    Raises:
        HTTPException: If file not found or processing error occurs
    """
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
    # Use the global ai_agent instance that was initialized at startup
    processor = JobProcessor(
        excel_path=settings.EXCEL_FILE_PATH,
        ai_agent=ai_agent,
        timeout=settings.REQUEST_TIMEOUT
    )
    
    # Collect all rows from incremental processing
    rows = []
    for row in processor.process_jobs_incrementally():
        rows.append(row)
    
    table = Table(rows=rows)
    
    logger.info(f"Successfully processed {len(table.rows)} job entries")
    return table


async def _process_and_callback():
    """
    Process jobs and send results to frontend callback URL.
    Runs in background task.
    """
    try:
        logger.info("Background job processing started")
        table = await _process_jobs()
        
        # Send results to frontend via POST
        logger.info(f"Sending results to frontend callback: {settings.FRONTEND_CALLBACK_URL}")
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.FRONTEND_CALLBACK_URL,
                json=table.model_dump(mode='json')
            )
            if response.status_code == 200:
                logger.info("Successfully sent results to frontend")
            else:
                logger.error(f"Failed to send results to frontend: {response.status_code}")
    except Exception as e:
        logger.error(f"Error in background processing: {str(e)}")


@app.get("/jobs")
async def get_jobs(background_tasks: BackgroundTasks):
    """
    Trigger job processing asynchronously.
    
    This endpoint:
    - Starts job processing in the background
    - Returns immediately with processing status
    - Sends completed results to configured frontend callback URL via POST
    
    Returns:
        Status indicating that processing has started
    """
    try:
        # Verify Excel file exists before starting background task
        if not os.path.exists(settings.EXCEL_FILE_PATH):
            raise HTTPException(
                status_code=404,
                detail=f"Excel file not found at {settings.EXCEL_FILE_PATH}"
            )
        
        # Add background task to process jobs and send callback
        background_tasks.add_task(_process_and_callback)
        
        logger.info("Job processing task added to background queue")
        return {
            "status": "processing",
            "message": "Job processing started. Results will be sent to frontend callback when complete.",
            "callback_url": settings.FRONTEND_CALLBACK_URL
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting job processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG_MODE
    )
