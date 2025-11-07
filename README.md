# superclaims-backend

What This System Does (In Simple Terms)
Your system is like a smart document reader. It:

  1.Receives: Medical documents (PDF files)
  
  2.Understands: What type of document it is (bill, discharge, or insurance card)
  
  3.Extracts: Important information from the document
  
  4.Validates: Checks if all data is correct and consistent
  
  5.Decides: Whether to approve, reject, or review the claim

  6.Returns: A structured response with all findings
  
Simple Architecture (3 Main Parts)

  Part 1: Input Layer
    User uploads PDFs
        ↓
    API receives files
        ↓
    Validates files (are they PDFs? are they valid?)

  Part 2: Processing Layer (The Brain)
    Orchestrator (Main Coordinator)
        ↓
    ┌───────────────────────────────────┐
    ↓           ↓           ↓           ↓
Classifier  PDF Service  BillAgent   DischargeAgent
(What type) (Extract text) (Extract) (Extract)
    │           │           │           │
    └───────────────────────────────────┘
         ↓
    IDCardAgent
    (Extract insurance info)
         ↓
    ValidatorAgent
    (Check consistency)
    
Part 3: Output Layer

  Decision Logic
(Approved? Rejected? Pending?)
        ↓
Return JSON Response
        ↓
Client receives structured data


How It Works (Step-by-Step)
  Step 1: User Uploads PDF
          curl -X POST /process-claim \
          -F "files=@medical_bill.pdf"

          The system receives your PDF file.

  Step 2: Classifier Determines Type
          Classifier Agent asks:
          "Is this a BILL, DISCHARGE SUMMARY, or ID CARD?"
  
          Logic: 
          - Looks at filename (bill, invoice, discharge, id, card)
          - If unsure → asks AI LLM
          - Returns type: "bill" OR "discharge_summary" OR "id_card"
  
            Example:
            Input: "hospital_discharge_summary.pdf"
            Output: "discharge_summary" 

  Step 3: Extract Text from PDF
          PDFService sends PDF to Google Gemini API
          Gemini extracts all text from the document
          System gets back readable text
          
          Example Input (PDF):
          ┌─────────────────────────┐
          │ APOLLO HOSPITAL BILL    │
          │ Patient: John Doe       │
          │ Amount: ₹50,000         │
          │ Date: 01-Jan-2025       │
          └─────────────────────────┘
          
          Example Output (Text):
          "APOLLO HOSPITAL BILL
          Patient: John Doe
          Amount: 50000
          Date: 01-Jan-2025
          ..."
  Step 4: Specialist Agent Extracts Data
     Depending on document type, use the right agent:
         If it's a BILL → BillAgent:
                   BillAgent receives the extracted text
                    Asks AI LLM: "Extract these fields:
                    - hospital_name
                    - total_amount
                    - date_of_service
                    - patient_name
                    - bill_items
                    
                    Return as JSON"
                    
                    Output:
                    {
                      "type": "bill",
                      "hospital_name": "Apollo Hospital",
                      "total_amount": 50000,
                      "date_of_service": "2025-01-01",
                      "patient_name": "John Doe",
                      "bill_items": ["Surgery", "Room Charges", ...]
                    }
        If it's a DISCHARGE SUMMARY → DischargeAgent:
                    DischargeAgent asks AI LLM: "Extract:
                    - patient_name
                    - diagnosis
                    - admission_date
                    - discharge_date
                    - treating_doctor
                    - procedures"
                    
                    Output:
                    {
                      "type": "discharge_summary",
                      "patient_name": "John Doe",
                      "diagnosis": "Appendicitis",
                      "admission_date": "2025-01-01",
                      "discharge_date": "2025-01-05",
                      "treating_doctor": "Dr. Smith",
                      "procedures": ["Appendectomy"]
                    }
          If it's an ID CARD → IDCardAgent:
                    IDCardAgent asks AI LLM: "Extract:
                      - patient_name
                      - policy_number
                      - member_id
                      - insurance_provider"
                      
                      Output:
                      {
                        "type": "id_card",
                        "patient_name": "John Doe",
                        "policy_number": "POL123456",
                        "member_id": "MEM789",
                        "insurance_provider": "ABC Insurance"
                      }

  Step 5: Validator Checks Everything
    ValidatorAgent checks:

    Check 1: Are required documents present?
            ✓ Do we have a BILL?
            ✓ Do we have a DISCHARGE SUMMARY?
            ✓ Do we have an ID CARD?
            
            If ANY are missing:
            Result: "REJECTED" (missing required documents)
    Check 2: Do patient names match?
            Bill says: "John Doe"
            Discharge says: "John Doe"
            ID says: "John Doe"
            Result: ✓ Names match - PASS
            
            Bill says: "John Doe"
            Discharge says: "Jane Doe"
            Result: ✗ Names don't match - FAIL (discrepancy detected)
    Check 3: Are dates logical?
            Admission: 2025-01-01
            Discharge: 2025-01-05
            Result: ✓ Discharge is AFTER admission - PASS
            
            Admission: 2025-01-05
            Discharge: 2025-01-01
            Result: ✗ Discharge is BEFORE admission - FAIL



 Return Response
        {
  "documents": [
    {
      "type": "bill",
      "hospital_name": "Apollo Hospital",
      "total_amount": 50000,
      ...
    },
    {
      "type": "discharge_summary",
      "patient_name": "John Doe",
      ...
    },
    {
      "type": "id_card",
      "patient_name": "John Doe",
      ...
    }
  ],
  "validation": {
    "missing_documents": [],
    "discrepancies": []
  },
  "claim_decision": {
    "status": "approved",
    "reason": "All documents present and verified",
    "confidence_score": 0.95
  }
}

 Simple Analogy
1. RECEPTIONIST (main.py)
   → Receives PDF documents from customer

2. SORTER (classifier_agent.py)
   → Looks at documents: "This is a bill, this is a discharge letter"

3. SCANNER (pdf_service.py)
   → Scans documents to extract text

4. DATA ENTRY TEAMS (bill_agent.py, discharge_agent.py, id_card_agent.py)
   → Each team specializes in one document type
   → Extracts relevant information into a form

5. QUALITY CHECKER (validator_agent.py)
   → Checks if all forms are filled correctly
   → Verifies names match, dates make sense, amounts are valid

6. MANAGER (Decision Logic)
   → Reviews quality checker's report
   → Makes final decision: Approved? Rejected? Need more review?

7. REPORT GENERATOR (main.py output)
   → Sends final decision back to customer as JSON
            

            


Key Concepts:

  Instead of ONE program doing everything,
  we have MULTIPLE SPECIALIZED agents:
  - Each does ONE job well
  - They coordinate through Orchestrator
  - Like a team with specialists
                



Orchestrator Pattern:
  
  The Orchestrator is like a PROJECT MANAGER:
- Receives the task
- Assigns work to appropriate agents
- Collects results
- Makes final decision

  






