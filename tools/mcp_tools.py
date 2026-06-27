from utils.mcp_client import query_mcp_ehr

async def fetch_ehr_medical_history(patient_id: str) -> str:
    """
    Query the isolated Electronic Health Records (EHR) server to find a patient's 
    centralized clinical profile, active allergies, existing diagnoses, and medications.
    Call this tool immediately if a patient asks what medications they are on, or to verify system allergy locks.
    """
    print(f"\n[TOOL CALLED] Agent requesting EHR lookup for patient code: '{patient_id}'")

    # Pass the execution directly across the MCP protocol pipeline
    ehr_response = await query_mcp_ehr(patient_id)
    return ehr_response