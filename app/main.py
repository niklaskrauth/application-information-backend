from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import logging
import os
import json
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


@app.get("/jobs/stream")
async def get_jobs_stream():
    """
    Process company entries from Excel and stream job information as they are processed.
    
    This endpoint provides incremental results, processing one company at a time:
    - Scrapes each website
    - Sends to AI for analysis
    - Streams the result
    - Then moves to the next company
    
    This approach is more efficient as results are available immediately rather than
    waiting for all companies to be processed.
    
    Returns:
        Streaming response with job information
    """
    try:
        # Check if Excel file exists
        if not os.path.exists(settings.EXCEL_FILE_PATH):
            raise HTTPException(
                status_code=404,
                detail=f"Excel file not found at {settings.EXCEL_FILE_PATH}"
            )

        # Create processor
        processor = JobProcessor(
            excel_path=settings.EXCEL_FILE_PATH,
            timeout=settings.REQUEST_TIMEOUT
        )
        
        async def generate():
            """Generate streaming response"""
            rows = []
            
            # Start JSON response
            yield '{"rows": ['
            
            first = True
            for row in processor.process_jobs_incrementally():
                if not first:
                    yield ','
                first = False
                
                # Convert TableRow to dict for JSON serialization
                row_dict = row.model_dump(mode='json')
                yield json.dumps(row_dict)
                rows.append(row)
            
            # End JSON response
            yield ']}'
            
            logger.info(f"Successfully streamed {len(rows)} job entries")
        
        return StreamingResponse(
            generate(),
            media_type="application/json"
        )
        
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
