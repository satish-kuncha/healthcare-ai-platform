# scheduling_tools.py
from pydantic_ai import RunContext
from models.context import PatientContext
from langfuse import observe


@observe(as_type="tool")
async def get_available_slots(ctx: RunContext[PatientContext], day: str):
    """Retrieve available appointment slots for a specific day."""
    patient = ctx.deps
    print(f"\n[TOOL RUNNING] checking slots for day: {day} (Patient: {patient.patient_name})")
    return {"day": day, "slots": ["10:00 AM", "2:00 PM", "4:00 PM"]}

#async def book_appointment(ctx: RunContext[PatientContext], slot: str):
#    """Book an appointment for the context patient at a chosen slot time."""
#    patient = ctx.deps
#    if not patient.patient_name:
#        return {"success": False, "error": "Missing patient identity context."}
#    
#    print(f"\n[TOOL RUNNING] book_appointment for {patient.patient_name} at {slot}")
#    return {"success": True, "confirmation": "APT12345", "slot": slot}

@observe(as_type="tool")
async def book_appointment(patient_name: str, day: str, time: str):
    """The REAL, pure API execution. Notice it doesn't use RunContext or know about the agent."""
    print(f"\n[SYSTEM API] Executing real database booking for {patient_name} on {day} at {time}")
    return {"success": True, "confirmation": "APT12345"}

@observe(as_type="tool")
async def cancel_appointment(ctx: RunContext[PatientContext], confirmation: str):
    """Cancel an existing appointment using a confirmation token."""
    print(f"\n[TOOL RUNNING] cancel_appointment tokens: {confirmation}")
    return {"cancelled": True}

@observe(as_type="tool")
async def stage_appointment_booking(ctx: RunContext[PatientContext], day: str, time: str):
    """Draft an appointment for manager review. Use this when the user wants to book."""
    ctx.deps.pending_booking_day = day
    ctx.deps.pending_booking_time = time
    print(f"\n[AGENT THOUGHT] Staging booking for {day} at {time} for manager review.")
    return f"Booking drafted for {day} at {time}. Tell the user you are waiting for manager approval."

