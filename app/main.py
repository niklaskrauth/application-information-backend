from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os
from pathlib import Path
from app.config import settings
from app.models import ProcessingResponse
from app.services.processor import ApplicationProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG_MODE else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Application Information Backend",
    description="Backend API for extracting information from website applications using AI",
    version="1.0.0"
)

# Configure CORS for frontend communication
# TODO: In production, replace ["*"] with specific frontend origins
# Example: allow_origins=["https://yourfrontend.com", "https://app.yourfrontend.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development only - configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Application Information Backend API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "openai_configured": bool(settings.OPENAI_API_KEY)
    }


@app.post("/process", response_model=ProcessingResponse)
async def process_applications():
    """
    Process all applications from the Excel file.
    
    This endpoint reads the Excel file, scrapes websites, extracts content from PDFs and images,
    and uses AI to analyze and summarize the information.
    
    Returns:
        ProcessingResponse with all extracted application information in JSON format
    """
    try:
        # Check if Excel file exists
        if not os.path.exists(settings.EXCEL_FILE_PATH):
            raise HTTPException(
                status_code=404,
                detail=f"Excel file not found at {settings.EXCEL_FILE_PATH}"
            )
        
        # Create processor and process applications
        processor = ApplicationProcessor(
            excel_path=settings.EXCEL_FILE_PATH,
            timeout=settings.REQUEST_TIMEOUT
        )
        
        results = processor.process_all_applications()
        
        return ProcessingResponse(
            success=True,
            message=f"Successfully processed {len(results)} applications",
            data=results
        )
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error processing applications: {str(e)}")
        return ProcessingResponse(
            success=False,
            message="Error processing applications",
            error=str(e)
        )


@app.post("/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    """
    Upload a new Excel file with website applications.
    
    Expected Excel format:
    - Column 'id': Unique identifier (integer)
    - Column 'name': Application name (string)
    - Column 'url': Website URL (string)
    - Column 'description': Optional description (string)
    """
    try:
        # Ensure data directory exists
        data_dir = Path(settings.EXCEL_FILE_PATH).parent
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded file
        file_path = settings.EXCEL_FILE_PATH
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Excel file uploaded successfully to {file_path}")
        
        return {
            "success": True,
            "message": "Excel file uploaded successfully",
            "file_path": file_path
        }
        
    except Exception as e:
        logger.error(f"Error uploading Excel file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/applications")
async def get_applications():
    """
    Get list of applications from Excel file without processing.
    
    Returns basic information from the Excel sheet.
    """
    try:
        from app.services.excel_reader import ExcelReader
        
        if not os.path.exists(settings.EXCEL_FILE_PATH):
            raise HTTPException(
                status_code=404,
                detail=f"Excel file not found at {settings.EXCEL_FILE_PATH}"
            )
        
        reader = ExcelReader(settings.EXCEL_FILE_PATH)
        entries = reader.read_entries()
        
        return {
            "success": True,
            "count": len(entries),
            "applications": [entry.model_dump() for entry in entries]
        }
        
    except Exception as e:
        logger.error(f"Error reading applications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG_MODE
    )
