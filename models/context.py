# context.py
import re
from datetime import date
from pydantic import BaseModel, Field, field_validator

class PatientContext(BaseModel):
    patient_name: str | None = Field(default=None, description="The full name of the patient.")
    dob: str | None = Field(default=None, description="Date of birth (YYYY-MM-DD).")
    member_id: str | None = Field(default=None, description="Insurance policy or member identification string.")
    appointment_day: str | None = Field(default=None, description="Requested day for an appointment.")
    preferred_slot: str | None = Field(default=None, description="Preferred time slot for the appointment.")
    # PRODUCTION PATTERN: Staging area for intents
    pending_booking_day: str | None = None
    pending_booking_time: str | None = None

    @field_validator("dob")
    @classmethod
    def validate_dob(cls, value: str | None) -> str | None:
        if not value:
            return value
            
        # 1. Regex check for YYYY-MM-DD format
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
            raise ValueError("DOB must be in strict YYYY-MM-DD format.")
            
        # 2. Check if the date is in the future
        parsed_date = date.fromisoformat(value)
        if parsed_date > date.today():
            raise ValueError("DOB cannot be a future date.")
            
        return value

    @field_validator("member_id")
    @classmethod
    def validate_member_id(cls, value: str | None) -> str | None:
        if not value:
            return value
            
        # Enforce that all insurance IDs must follow the format: INS-XXXXX
        if not value.startswith("INS-") or not value[4:].isdigit():
            raise ValueError("Invalid Member ID format. It must follow the pattern 'INS-' followed by digits (e.g., INS-12345).")
            
        return value
