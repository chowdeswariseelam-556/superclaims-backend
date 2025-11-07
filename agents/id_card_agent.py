"""
ID_CARD_AGENT - agents/id_card_agent.py
Save this file as: superclaims-backend/agents/id_card_agent.py
"""
from services.llm_service import LLMService
from models.schemas import IDCardDocument
from utils.helpers import setup_logging
logger = setup_logging()
class IDCardAgent:
    """Agent specialized in extracting data from insurance ID cards"""
    
    def __init__(self):
       
        self.llm_service = LLMService()
    
    async def process(self, text: str, filename: str):
        
        
        system_prompt = """You are an expert at extracting information from insurance ID cards.
Extract and return ONLY valid JSON (no markdown):
{
    "type": "id_card",
    "patient_name": "full patient name",
    "policy_number": "policy number",
    "member_id": "member/subscriber ID",
    "insurance_provider": "insurance company name or null"
}"""
        
        prompt = f"""Extract data from this insurance ID card:

{text[:3000]}

Return valid JSON only."""
        
        try:
            response = await self.llm_service.get_structured_output(
                prompt=prompt,
                system_prompt=system_prompt,
                schema=IDCardDocument.model_json_schema()
            )
            logger.info(f"✅ IDCardAgent: Extracted ID card data from {filename}")
            return IDCardDocument(**response)
        except Exception as e:
            logger.error(f"❌ IDCardAgent error: {str(e)}")
            return IDCardDocument(
                type="id_card",
                patient_name="Unknown",
                policy_number="UNKNOWN",
                member_id="UNKNOWN"
            )