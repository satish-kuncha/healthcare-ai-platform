# insurance_tools.py
from pydantic_ai import RunContext
from models.context import PatientContext

async def verify_coverage(ctx: RunContext[PatientContext]):
    """Verify insurance coverage details using the context member ID."""
    patient = ctx.deps
    if not patient.member_id:
        return {"error": "No member ID found in context to verify."}
    
    print(f"\n[TOOL RUNNING] verify_coverage for member_id: {patient.member_id}")
    return {"covered": True, "copay": 25}

async def check_eligibility(ctx: RunContext[PatientContext]):
    """Check general healthcare program eligibility for the context member ID."""
    patient = ctx.deps
    if not patient.member_id:
        return {"error": "No member ID found in context to check eligibility."}
        
    print(f"\n[TOOL RUNNING] check_eligibility for member_id: {patient.member_id}")
    return {"eligible": True}