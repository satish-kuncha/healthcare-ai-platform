import os
import sys
import json
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server named "EHR-Gateway"
mcp_server = FastMCP("EHR-Gateway")

# Path to the mock healthcare record database
DB_PATH = os.path.join(os.path.dirname(__file__), "ehr_db.json")

def load_ehr_data():
    if not os.path.exists(DB_PATH):
        return {"patients": {}}
    with open(DB_PATH, "r") as f:
        return json.load(f)

@mcp_server.tool()
def get_patient_medical_history(patient_id: str) -> str:
    """
    Retrieve clinical medical history, existing diagnoses, active allergies, 
    and current medications for a patient using their unique Patient ID (e.g., PT-8831).
    """
    print(f"\n[MCP SERVER EXECUTING] Tool 'get_patient_medical_history' called for ID: {patient_id}",file=sys.stderr)
    
    db = load_ehr_data()
    patient = db.get("patients", {}).get(patient_id)
    
    if not patient:
        return f"Error: Patient record for ID '{patient_id}' could not be located in the secure EHR registry."
    
    # Format the clinical data into a clear profile response string
    history_summary = (
        f"Clinical Summary for {patient['name']} ({patient_id}):\n"
        f"- Diagnosed Conditions: {', '.join(patient['conditions'])}\n"
        f"- Known Drug Allergies: {', '.join(patient['allergies'])}\n"
        f"- Active Prescriptions: {', '.join(patient['current_medications'])}"
    )
    return history_summary

if __name__ == "__main__":
    # Start the server using the standard 'stdio' communication transport layer
    print("Initializing Secure Healthcare MCP Server via Standard I/O...",file=sys.stderr)
    mcp_server.run(transport="stdio")