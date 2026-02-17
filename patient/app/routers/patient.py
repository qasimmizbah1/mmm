from fastapi import APIRouter, HTTPException, Request, Depends
from models import UserRole, ReferralCreate, DoctorProfileCreate
from uuid import UUID

from services.patient_service import doctor_profile_service, view_profile_service

router = APIRouter(prefix="/v1/patient", tags=["Manage Users"])



   

@router.post("/profile")
async def create_doctor_profile(
    data: DoctorProfileCreate,
    request: Request,
):
    
    return await doctor_profile_service(data, request)


@router.get("/me/{patient_id}")
async def view_patient_profile(
    patient_id: UUID,
    request: Request,
):
    
    return await view_profile_service(patient_id, request)

  
