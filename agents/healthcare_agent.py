# unified_agent.py
from pydantic_ai import Agent
from models.context import PatientContext

# Import your mock tools directly
from tools.scheduling_tools import get_available_slots, book_appointment, cancel_appointment, stage_appointment_booking
from tools.insurance_tools import verify_coverage, check_eligibility
# Assuming you put update_patient_record in a file called context_tools.py
from tools.context_tools import update_patient_record

healthcare_agent = Agent(
    "google:gemini-2.5-flash-lite",
    deps_type=PatientContext,
    tools=[
        update_patient_record,
        get_available_slots,
        stage_appointment_booking, # The LLM stages the intent
        cancel_appointment,
        verify_coverage,
        check_eligibility
    ],
    system_prompt=(
        "You are an advanced healthcare operations assistant.\n\n"
        "CRITICAL RULES:\n"
        "1. If the user provides personal info (name, DOB, member ID), IMMEDIATELY call `update_patient_record`.\n"
        "2. Always check the patient context (`deps`) before executing insurance tools.\n"
        "3. To book an appointment, use `stage_appointment_booking`. "
        "4. Never promise the booking is finalized until you receive a SYSTEM OVERRIDE confirmation."
        "5. If a tool requires data missing from context, ask the user for it instead of guessing.\n"
        "6. You can execute multiple tools in sequence (e.g., update the record, then check slots)."
    )
)