"""
Superclaims Backend - Medical Insurance Claim Document Processor
FastAPI application with AI-driven agentic workflows

USAGE:
    python main.py
    
Then visit: http://localhost:8000/docs
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import asyncio
from pathlib import Path
import tempfile
import os
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.orchestrator import ClaimOrchestrator
from models.schemas import ClaimProcessingResponse
from utils.helpers import validate_pdf_files, setup_logging

# Initialize FastAPI app
app = FastAPI(
    title="Superclaims Backend API",
    description="AI-Driven Medical Insurance Claim Document Processor",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Setup logging
logger = setup_logging()

# Initialize orchestrator
try:
    orchestrator = ClaimOrchestrator()
    logger.info("✅ ClaimOrchestrator initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize orchestrator: {str(e)}")
    orchestrator = None

@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "active",
        "service": "Superclaims Backend",
        "version": "1.0.0",
        "message": "Visit /docs for API documentation"
    }

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "orchestrator": "initialized" if orchestrator else "failed",
        "agents": {
            "classifier": "ready",
            "bill": "ready",
            "discharge": "ready",
            "id_card": "ready",
            "validator": "ready"
        },
        "api_docs": "http://localhost:8000/docs"
    }

@app.post("/process-claim", response_model=ClaimProcessingResponse)
async def process_claim(
    files: List[UploadFile] = File(..., description="Multiple PDF files (bill, ID card, discharge summary)")
):
    """
    Process medical insurance claim documents using AI agents.
    
    Steps:
    1. Validates uploaded PDF files
    2. Classifies each PDF using LLM-based agent
    3. Extracts text using Google Gemini API
    4. Processes extracted text using specialized agents
    5. Structures output into defined JSON schema
    6. Validates data for missing info or inconsistencies
    7. Returns final claim decision (approve/reject/pending)
    
    Args:
        files: List of PDF files to process (bill, discharge summary, insurance ID)
        
    Returns:
        ClaimProcessingResponse with documents, validation, and decision
        
    Example:
        curl -X POST http://localhost:8000/process-claim \\
          -F "files=@bill.pdf" \\
          -F "files=@discharge.pdf" \\
          -F "files=@id_card.pdf"
    """
    if not orchestrator:
        raise HTTPException(
            status_code=503,
            detail="Orchestrator not initialized. Check API keys and configuration."
        )
    
    try:
        logger.info(f"📄 Processing {len(files)} files")
        
        # Validate uploaded files
        await validate_pdf_files(files)
        
        # Create temporary directory for file processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save uploaded files temporarily
            file_paths = []
            for file in files:
                file_path = Path(temp_dir) / file.filename
                content = await file.read()
                with open(file_path, "wb") as f:
                    f.write(content)
                file_paths.append({
                    "path": str(file_path),
                    "filename": file.filename
                })
                logger.info(f"📦 Saved: {file.filename} ({len(content)} bytes)")
            
            # Process claim through orchestrator
            logger.info("🤖 Starting orchestrator processing...")
            result = await orchestrator.process_claim(file_paths)
            
            logger.info("✅ Claim processing completed successfully")
            return result
            
    except ValueError as ve:
        logger.error(f"❌ Validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"❌ Error processing claim: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"❌ Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Superclaims Backend Server...")
    logger.info("📖 API Docs: http://localhost:8000/docs")
    logger.info("🏥 Process Claims: POST http://localhost:8000/process-claim")
    uvicorn.run(app, host="0.0.0.0", port=8000)