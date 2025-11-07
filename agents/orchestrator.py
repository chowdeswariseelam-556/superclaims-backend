"""
agents/orchestrator.py - Main orchestrator for coordinating multiple AI agents
Implements supervisor pattern for multi-agent workflow
"""
import asyncio
from typing import List, Dict
import json

from agents.classifier_agent import ClassifierAgent
from agents.bill_agent import BillAgent
from agents.discharge_agent import DischargeAgent
from agents.id_card_agent import IDCardAgent
from agents.validator_agent import ValidatorAgent
from services.pdf_service import PDFService
from models.schemas import ClaimProcessingResponse, ValidationResult, ClaimDecision
from utils.helpers import setup_logging

logger = setup_logging()

class ClaimOrchestrator:
    """
    Orchestrator agent that coordinates specialized agents.
    Implements the supervisor pattern - central coordinator that:
    1. Classifies documents
    2. Extracts text from PDFs
    3. Routes to appropriate specialist agents
    4. Validates results
    5. Makes final decision
    """
    
    def __init__(self):
        """Initialize all agents and services"""
        try:
            self.pdf_service = PDFService()
            self.classifier_agent = ClassifierAgent()
            self.bill_agent = BillAgent()
            self.discharge_agent = DischargeAgent()
            self.id_card_agent = IDCardAgent()
            self.validator_agent = ValidatorAgent()
            logger.info("✅ ClaimOrchestrator: All agents initialized")
        except Exception as e:
            logger.error(f"❌ ClaimOrchestrator initialization error: {str(e)}")
            raise
    
    async def process_claim(self, file_paths: List[Dict]) -> ClaimProcessingResponse:
        """
        Main orchestration method - processes claim through all agents
        
        Args:
            file_paths: List of dicts with 'path' and 'filename' keys
            
        Returns:
            ClaimProcessingResponse with documents, validation, and decision
        """
        logger.info(f"🤖 Orchestrator: Starting claim processing for {len(file_paths)} files")
        
        try:
            # Step 1: Classify documents
            logger.info("📋 Step 1: Classifying documents...")
            classifications = await self._classify_documents(file_paths)
            logger.info(f"✅ Classifications: {classifications}")
            
            # Step 2: Extract text from all PDFs concurrently
            logger.info("📄 Step 2: Extracting text from PDFs...")
            extraction_tasks = [
                self.pdf_service.extract_text(fp["path"]) 
                for fp in file_paths
            ]
            extracted_texts = await asyncio.gather(*extraction_tasks)
            logger.info(f"✅ Extracted text from {len(extracted_texts)} PDFs")
            
            # Step 3: Process each document with appropriate agent
            logger.info("🔍 Step 3: Processing documents with specialist agents...")
            documents = []
            for i, (file_info, classification, text) in enumerate(
                zip(file_paths, classifications, extracted_texts)
            ):
                logger.info(f"  Processing ({i+1}/{len(file_paths)}): {classification} - {file_info['filename']}")
                doc_data = await self._route_to_agent(classification, text, file_info['filename'])
                if doc_data:
                    documents.append(doc_data)
                    logger.info(f"  ✅ Processed: {classification}")
            
            logger.info(f"✅ Processed {len(documents)} documents")
            
            # Step 4: Validate all extracted data
            logger.info("✔️ Step 4: Validating data...")
            validation_result = await self.validator_agent.validate(documents)
            logger.info(f"✅ Validation complete: {len(validation_result.discrepancies)} issues found")
            
            # Step 5: Make final claim decision
            logger.info("⚖️ Step 5: Making final decision...")
            claim_decision = await self._make_decision(documents, validation_result)
            logger.info(f"✅ Decision: {claim_decision.status}")
            
            # Prepare response
            response = ClaimProcessingResponse(
                documents=documents,
                validation=validation_result,
                claim_decision=claim_decision,
                processing_metadata={
                    "total_files_processed": len(file_paths),
                    "document_types_found": [d.type for d in documents],
                    "validation_status": "passed" if not validation_result.discrepancies else "issues_found"
                }
            )
            
            logger.info("🎉 Orchestrator: Claim processing completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"❌ Orchestrator error: {str(e)}", exc_info=True)
            raise
    
    async def _classify_documents(self, file_paths: List[Dict]) -> List[str]:
        """Classify each PDF using the classifier agent"""
        logger.debug(f"Classifying {len(file_paths)} documents...")
        tasks = [
            self.classifier_agent.classify(fp["filename"], fp["path"])
            for fp in file_paths
        ]
        return await asyncio.gather(*tasks)
    
    async def _route_to_agent(self, doc_type: str, text: str, filename: str):
        """Route document to appropriate specialist agent based on type"""
        agent_map = {
            "bill": self.bill_agent,
            "discharge_summary": self.discharge_agent,
            "id_card": self.id_card_agent
        }
        
        agent = agent_map.get(doc_type)
        if agent:
            try:
                return await agent.process(text, filename)
            except Exception as e:
                logger.error(f"❌ Error in {doc_type} agent: {str(e)}")
                return None
        else:
            logger.warning(f"⚠️ Unknown document type: {doc_type}")
            return None
    
    async def _make_decision(
        self, 
        documents: List, 
        validation: ValidationResult
    ) -> ClaimDecision:
        """
        Make final claim decision based on documents and validation
        
        Logic:
        - Missing documents → REJECTED
        - Data discrepancies → PENDING_REVIEW
        - All required docs + no issues → APPROVED
        - Incomplete docs → REJECTED
        """
        
        doc_types = {doc.type for doc in documents}
        required_types = {"bill", "discharge_summary", "id_card"}
        
        # Check for missing documents
        if validation.missing_documents:
            logger.warning(f"Missing documents: {validation.missing_documents}")
            return ClaimDecision(
                status="rejected",
                reason=f"Missing required documents: {', '.join(validation.missing_documents)}",
                confidence_score=1.0
            )
        
        # Check for data discrepancies
        if validation.discrepancies:
            logger.warning(f"Data discrepancies found: {validation.discrepancies}")
            return ClaimDecision(
                status="pending_review",
                reason=f"Data discrepancies found - manual review required: {'; '.join(validation.discrepancies[:2])}",
                confidence_score=0.6
            )
        
        # Check if all required documents are present
        if doc_types >= required_types:
            logger.info("✅ All required documents present and validated")
            return ClaimDecision(
                status="approved",
                reason="All required documents present and data is consistent",
                confidence_score=0.95
            )
        
        # Fallback: Incomplete
        logger.warning("Incomplete documentation")
        return ClaimDecision(
            status="rejected",
            reason="Incomplete documentation",
            confidence_score=0.8
        )