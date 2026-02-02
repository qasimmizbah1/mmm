from pydantic import BaseModel, Field, UUID4, EmailStr
from uuid import UUID
from typing import Literal
from datetime import datetime, date
import re
from typing import Optional, Dict, Any, Literal, List



class UserRole(BaseModel):
    role: Literal['patient', 'therapist']
