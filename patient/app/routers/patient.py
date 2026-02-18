from fastapi import APIRouter, HTTPException, Request, Depends, UploadFile, File, Form
from models import PatientProfileCreate
from uuid import UUID
from typing import Optional


from services.patient_service import patient_profile_service, view_profile_service, view_medical_history_service

router = APIRouter(prefix="/v1/patient", tags=["Manage Patient Profiles"])

@router.post("/profile")
async def create_patient_profile(
    request: Request,
    patient_id: str = Form(...),
    phone: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    dob: Optional[str] = Form(None),
    profile_image: Optional[UploadFile] = File(None),
):
    
    return await patient_profile_service(request,patient_id,phone,gender,dob,profile_image)


@router.get("/me/{patient_id}")
async def view_patient_profile(
    patient_id: UUID,
    request: Request,
):
    
    return await view_profile_service(patient_id, request)


#view medical history
@router.get("/medical-history/{patient_id}")
async def view_medical_history(patient_id: UUID, request: Request):
    return await view_medical_history_service(patient_id, request)