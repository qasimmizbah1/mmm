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
    patient_id: int
    therapist_id: int

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
