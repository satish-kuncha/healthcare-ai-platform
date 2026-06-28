from pydantic_ai import RunContext
from pydantic import ValidationError
from models.context import PatientContext
from langfuse import observe

@observe(as_type="tool")
def update_patient_record(
    ctx: RunContext[PatientContext], 
    patient_name: str | None = None, 
    dob: str | None= None, 
    member_id: str | None= None
):
    """
    Update the system's business state with patient information.
    Call this ANY TIME the user provides their name, DOB, or member ID.
    """
    try:
        # Create a temporary copy of current context data to validate the incoming fields
        current_data = ctx.deps.model_dump()
        
        if patient_name:
            current_data["patient_name"] = patient_name
        if dob:
            current_data["dob"] = dob
        if member_id:
            current_data["member_id"] = member_id
            
        # Trigger Pydantic's verification mechanisms
        validated = PatientContext(**current_data)
        
        # If valid, apply changes to live state
        ctx.deps.patient_name = validated.patient_name
        ctx.deps.dob = validated.dob
        ctx.deps.member_id = validated.member_id
        
        print(f"\n[SYSTEM] State Validated & Updated -> Name: {ctx.deps.patient_name}, ID: {ctx.deps.member_id}")
        return "Business state updated successfully. Proceed with the user's request."

    except ValidationError as e:
        # Catch validation errors and collect the exact feedback message
        error_messages = [err["msg"] for err in e.errors()]
        combined_errors = "; ".join(error_messages)
        print(f"\n[SYSTEM VALIDATION BLOCKED] Errors: {combined_errors}")
        
        # Return the error message directly to the LLM so it can ask the user to fix it
        return f"Rejected context update due to validation errors: {combined_errors}. Please ask the patient to provide valid information."