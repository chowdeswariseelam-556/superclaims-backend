"""
utils/helpers.py - Utility functions and helpers
"""
import logging
from fastapi import UploadFile
from typing import List

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("superclaims")

async def validate_pdf_files(files: List[UploadFile]) -> bool:
    """Validate uploaded files"""
    if len(files) < 1:
        raise ValueError("❌ At least one PDF file required")
    
    MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
    
    for file in files:
        # Check extension
        if not file.filename.lower().endswith('.pdf'):
            raise ValueError(f"❌ '{file.filename}' is not a PDF")
        
        # Check filename
        if not file.filename:
            raise ValueError("❌ Invalid filename")
        
        # Check file size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            size_mb = len(content) / (1024 * 1024)
            raise ValueError(f"❌ '{file.filename}' exceeds 25MB ({size_mb:.2f}MB)")
        
        if len(content) == 0:
            raise ValueError(f"❌ '{file.filename}' is empty")
        
        # Reset pointer
        await file.seek(0)
    
    return True