from pydantic import BaseModel, Field, UUID4, EmailStr
from uuid import UUID
from typing import Literal
from datetime import datetime, date
import re
from typing import Optional, Dict, Any, Literal, List



class UserRole(BaseModel):
    role: Literal['patient', 'therapist']


from pydantic import BaseModel
from typing import Optional, Literal

class ReferralCreate(BaseModel):
    doctor_id: str
    patient_id: str
    therapist_id: str

    urgency_level: Literal[
        "Low", "Medium", "High", "Emergency"
    ]

    preferred_modality: Literal[
        "Therapy",
        "Psychiatric Assessment",
        "Both"
    ]

    clinical_presentation: str
    chief_complaint: str
    additional_requirements: Optional[str] = None

class PatientProfileCreate(BaseModel):
    patient_id: UUID
    phone: str
    gender: Literal["male", "female", "other"]
    dob: date


class InsuranceCreate(BaseModel):
    patient_id: UUID
    insurance_name: str
    policy_number: str
    coverage_details: str
    notes: Optional[str] = None

class UpdateInsurance(BaseModel):
    insurance_name: Optional[str] = None
    policy_number: Optional[str] = None
    coverage_details: Optional[str] = None
    notes: Optional[str] = None