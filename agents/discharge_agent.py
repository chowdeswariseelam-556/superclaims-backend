"""
DISCHARGE_AGENT - agents/discharge_agent.py
Save this file as: superclaims-backend/agents/discharge_agent.py
"""

from services.llm_service import LLMService
from models.schemas import DischargeSummaryDocument
from utils.helpers import setup_logging
logger = setup_logging()




class DischargeAgent:
    """Agent specialized in extracting data from discharge summaries"""
    
    def __init__(self):
        
        self.llm_service = LLMService()
    
    async def process(self, text: str, filename: str):
        
        
        system_prompt = """You are an expert at extracting information from hospital discharge summaries.
Extract and return ONLY valid JSON (no markdown):
{
    "type": "discharge_summary",
    "patient_name": "full patient name",
    "diagnosis": "primary diagnosis",
    "admission_date": "YYYY-MM-DD",
    "discharge_date": "YYYY-MM-DD",
    "treating_doctor": "doctor name or null",
    "procedures": ["procedure1", "procedure2"] or null
}"""
        
        prompt = f"""Extract data from this discharge summary:

{text[:3000]}

Return valid JSON only."""
        
        try:
            response = await self.llm_service.get_structured_output(
                prompt=prompt,
                system_prompt=system_prompt,
                schema=DischargeSummaryDocument.model_json_schema()
            )
            logger.info(f"✅ DischargeAgent: Extracted discharge data from {filename}")
            return DischargeSummaryDocument(**response)
        except Exception as e:
            logger.error(f"❌ DischargeAgent error: {str(e)}")
            return DischargeSummaryDocument(
                type="discharge_summary",
                patient_name="Unknown Patient",
                diagnosis="Unknown",
                admission_date="2024-01-01",
                discharge_date="2024-01-02"
            )