from pydantic import BaseModel, Field, UUID4, EmailStr
from uuid import UUID
from typing import Literal
from datetime import datetime, date
import re
from typing import Optional, Dict, Any, Literal, List
class PageBase(BaseModel):
    slug: str
    title: str
    content: str
    thumbnail: Optional[str] = None
    status: str = "draft"
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

class PageCreate(PageBase):
    pass

class PageUpdate(BaseModel):
    slug: str
    title: Optional[str] = None
    content: Optional[str] = None
    thumbnail: Optional[str] = None
    status: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None

class PageOutAll(BaseModel):
    id: int
    slug: str
    title: str
    thumbnail: Optional[str] = None
    status: str = "draft"
    created_at: datetime
    updated_at: datetime


class PageOut(PageBase):
    id: int
    created_at: datetime
    updated_at: datetime

class UserRequest(BaseModel):
    user_id: UUID4


class BuyerProfileData(BaseModel):
    name: str
    company_name: str 
    vat_number: str


class SupplierProfileData(BaseModel):
    name: str
    company_name: str
    kyc_status: str


LogLevel = Literal['DEBUG','INFO','WARNING','ERROR','CRITICAL','AUDIT']

class LogCreate(BaseModel):
    user_id: Optional[UUID4] = None
    level: LogLevel = 'INFO'
    action: str
    path: Optional[str] = None
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)

class LogOut(BaseModel):
    id: UUID4
    user_id: Optional[UUID4]
    level: LogLevel
    action: str
    path: Optional[str]
    ip: Optional[str]
    user_agent: Optional[str]
    meta: Dict[str, Any]
    created_at: datetime

class LogListOut(BaseModel):
    items: list[LogOut]
    page: int
    page_size: int
    total: int
    pages: int

class BuyerUpdate(BaseModel):
    is_active: Optional[bool] = None
    user_name: Optional[str] = None
    
    

class SupplierUpdate(BaseModel):
    is_active: Optional[bool] = None
    user_name: Optional[str] = None
    company_name: Optional[str] = None
    kyc_status: Optional[str] = None


class VehicleMake(BaseModel):
    name: str

class VehicleModel(BaseModel):
    make_id: UUID
    name: str

class VehicleTrim(BaseModel):
    make_id: UUID
    model_id: UUID
    year_from: Optional[int]
    year_to: Optional[int]
    trim: Optional[str]


class CommonDataIn(BaseModel):
    type: str
    data: Any

class MenuData(BaseModel):
    data: Any    


class CommonDataUpdate(BaseModel):
    type: Optional[str] = None
    data: Any


class PartRequestInDB(BaseModel):
    id: UUID
    status: int
    created_at: datetime
    updated_at: datetime


class StatusUpdate(BaseModel):
    status: int

class HomePageContent(BaseModel):
    section1: Dict[str, Any]
    section2: Dict[str, Any]
    section3: List[Dict[str, Any]]
    section4: Dict[str, Any]
    section5: Dict[str, Any]

class KycAttachment(BaseModel):
    id: UUID
    status: str


class kycActionModel(BaseModel):
    # kyc_id: UUID4
    # user_id: UUID4
    # type: Literal['approved', 'rejected', 'pending']
    user_id: UUID
    type: str   # approved / rejected
    attachment: List[KycAttachment]