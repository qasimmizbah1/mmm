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

class DoctorProfileCreate(BaseModel):
    doctor_id: UUID
    full_name: str
    license_number: str
    registration: str
    clinic_name: Optional[str] = None
    medical_field: str
    address: str
    phone: str
    gender: Literal["male", "female", "other"]
    dob: date

class MedicalHistory(BaseModel):
    patient_id: UUID
    doctor_id: UUID
    diagnosis: str
    treatment_plan: str
    medications: Optional[str] = None
    notes: Optional[str] = None

class updateMedicalHistory(BaseModel):
    diagnosis: str
    treatment_plan: str
    medications: Optional[str] = None
    notes: Optional[str] = None