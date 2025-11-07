from typing import List
from models.schemas import ValidationResult
from utils.helpers import setup_logging
from datetime import datetime

logger = setup_logging()

class ValidatorAgent:
    """Agent specialized in validating extracted claim data"""
    
    async def validate(self, documents: List) -> ValidationResult:
        """Validate documents for completeness and consistency"""
        missing_documents = []
        discrepancies = []
        
        # Check for required document types
        doc_types = {doc.type for doc in documents}
        required_types = {"bill", "discharge_summary", "id_card"}
        missing = required_types - doc_types
        
        if missing:
            missing_documents = list(missing)
            logger.warning(f"⚠️ Missing documents: {missing_documents}")
        
        # Extract patient names from each document
        patient_names = []
        for doc in documents:
            if hasattr(doc, 'patient_name') and doc.patient_name:
                patient_names.append((doc.type, doc.patient_name.lower().strip()))
        
        # Check name consistency
        if len(patient_names) > 1:
            unique_names = set(name for _, name in patient_names)
            if len(unique_names) > 1:
                discrepancies.append(f"Patient name mismatch across documents")
                logger.warning(f"⚠️ Name mismatch detected")
        
        # Check date logic
        discharge_doc = next((d for d in documents if d.type == "discharge_summary"), None)
        if discharge_doc:
            try:
                admission = datetime.strptime(discharge_doc.admission_date, "%Y-%m-%d")
                discharge = datetime.strptime(discharge_doc.discharge_date, "%Y-%m-%d")
                
                if discharge < admission:
                    discrepancies.append("Discharge date is before admission date")
                    logger.warning("⚠️ Date logic error detected")
            except Exception as e:
                logger.debug(f"Date parsing error: {e}")
        
        # Check bill amount validity
        bill_doc = next((d for d in documents if d.type == "bill"), None)
        if bill_doc:
            try:
                if bill_doc.total_amount <= 0:
                    discrepancies.append("Invalid bill amount (must be positive)")
                    logger.warning("⚠️ Invalid bill amount")
            except Exception as e:
                logger.debug(f"Bill amount check error: {e}")
        
        # Check ID card validity
        id_doc = next((d for d in documents if d.type == "id_card"), None)
        if id_doc:
            if not id_doc.policy_number or id_doc.policy_number == "UNKNOWN":
                discrepancies.append("Missing or invalid policy number")
                logger.warning("⚠️ Invalid policy number")
            
            if not id_doc.member_id or id_doc.member_id == "UNKNOWN":
                discrepancies.append("Missing or invalid member ID")
                logger.warning("⚠️ Invalid member ID")
        
        logger.info(f"✅ ValidatorAgent: Validation complete - {len(discrepancies)} issues")
        
        return ValidationResult(
            missing_documents=missing_documents,
            discrepancies=discrepancies
        )