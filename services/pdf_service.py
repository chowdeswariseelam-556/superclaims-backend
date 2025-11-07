"""
services/pdf_service.py - PDF text extraction using Google Gemini API
"""
import os
import pathlib
from utils.helpers import setup_logging

logger = setup_logging()

class PDFService:
    """Extract text from PDF files using Gemini"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY environment variable not set")
        
        try:
            import google.genai as genai
            self.client = genai.Client(api_key=api_key)
            logger.info("✅ PDFService: Gemini API initialized")
        except ImportError:
            raise ImportError("❌ google-genai not installed: pip install google-genai")
    
    async def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF using Gemini"""
        try:
            import google.genai as genai
            
            filepath = pathlib.Path(pdf_path)
            
            if not filepath.exists():
                raise FileNotFoundError(f"❌ PDF not found: {pdf_path}")
            
            if filepath.suffix.lower() != '.pdf':
                raise ValueError(f"❌ Not a PDF file: {pdf_path}")
            
            # Read PDF
            pdf_data = filepath.read_bytes()
            logger.info(f"📄 Extracting text from {filepath.name} ({len(pdf_data)} bytes)...")
            
            # Use Gemini
            prompt = "Extract ALL text content from this document. Include names, dates, amounts, diagnoses, etc."
            
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=[
                    genai.types.Part.from_bytes(
                        data=pdf_data,
                        mime_type='application/pdf',
                    ),
                    prompt
                ],
                config=genai.types.GenerateContentConfig(temperature=0.0)
            )
            
            extracted_text = response.text
            
            if not extracted_text or len(extracted_text.strip()) == 0:
                logger.warning(f"⚠️ No text extracted from {filepath.name}")
                extracted_text = "[PDF content could not be extracted]"
            
            logger.info(f"✅ Extracted {len(extracted_text)} chars from {filepath.name}")
            return extracted_text
            
        except Exception as e:
            logger.error(f"❌ PDF extraction error: {str(e)}")
            raise