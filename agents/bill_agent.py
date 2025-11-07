"""
BILL_AGENT - agents/bill_agent.py
Save this file as: superclaims-backend/agents/bill_agent.py
"""
from services.llm_service import LLMService
from models.schemas import BillDocument
from utils.helpers import setup_logging

logger = setup_logging()

class BillAgent:
    """Agent specialized in extracting data from medical bills"""
    
    def __init__(self):
        self.llm_service = LLMService()
    
    async def process(self, text: str, filename: str) -> BillDocument:
        """Extract structured data from medical bill text"""
        
        system_prompt = """You are an expert at extracting information from medical bills.
Extract and return ONLY valid JSON (no markdown):
{
    "type": "bill",
    "hospital_name": "hospital name",
    "total_amount": numeric_amount,
    "date_of_service": "YYYY-MM-DD",
    "patient_name": "patient name or null",
    "bill_items": ["item1", "item2"] or null
}"""
        
        prompt = f"""Extract data from this medical bill:

{text[:3000]}

Return valid JSON only."""
        
        try:
            response = await self.llm_service.get_structured_output(
                prompt=prompt,
                system_prompt=system_prompt,
                schema=BillDocument.model_json_schema()
            )
            logger.info(f"✅ BillAgent: Extracted bill data from {filename}")
            return BillDocument(**response)
        except Exception as e:
            logger.error(f"❌ BillAgent error: {str(e)}")
            return BillDocument(
                type="bill",
                hospital_name="Unknown Hospital",
                total_amount=0.0,
                date_of_service="2024-01-01"
            )





