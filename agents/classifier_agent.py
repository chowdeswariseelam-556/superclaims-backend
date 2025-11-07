"""
agents/classifier_agent.py - Document classification agent using LLM
"""
from services.llm_service import LLMService
from utils.helpers import setup_logging

logger = setup_logging()

class ClassifierAgent:
    """Agent specialized in classifying document types"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.system_prompt = """You are a document classification expert for medical insurance claims.
Given a filename, classify it into ONE of these types:
- bill: Medical bills, invoices, payment receipts
- discharge_summary: Hospital discharge summaries, medical reports
- id_card: Insurance ID cards, policy documents

Respond ONLY with: bill, discharge_summary, or id_card"""
    
    async def classify(self, filename: str, file_path: str = None) -> str:
        """Classify document based on filename"""
        filename_lower = filename.lower()
        
        # Fast filename-based classification
        if any(kw in filename_lower for kw in ['bill', 'invoice', 'payment', 'receipt']):
            logger.debug(f"✅ Classified '{filename}' as 'bill' (filename-based)")
            return "bill"
        
        if any(kw in filename_lower for kw in ['discharge', 'summary', 'report']):
            logger.debug(f"✅ Classified '{filename}' as 'discharge_summary' (filename-based)")
            return "discharge_summary"
        
        if any(kw in filename_lower for kw in ['id', 'card', 'policy', 'insurance']):
            logger.debug(f"✅ Classified '{filename}' as 'id_card' (filename-based)")
            return "id_card"
        
        # Fallback to LLM
        try:
            prompt = f"Classify this document: {filename}"
            classification = await self.llm_service.get_completion(
                prompt=prompt,
                system_prompt=self.system_prompt
            )
            classification = classification.strip().lower()
            valid_types = ["bill", "discharge_summary", "id_card"]
            if classification not in valid_types:
                logger.warning(f"Invalid classification '{classification}', defaulting to 'bill'")
                classification = "bill"
            logger.debug(f"✅ Classified '{filename}' as '{classification}' (LLM-based)")
            return classification
        except Exception as e:
            logger.error(f"❌ Classification error: {str(e)}, defaulting to 'bill'")
            return "bill"