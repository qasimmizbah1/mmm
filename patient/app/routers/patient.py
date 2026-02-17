from fastapi import APIRouter, HTTPException, Request, Depends
from models import PatientProfileCreate, InsuranceCreate, UpdateInsurance
from uuid import UUID

from services.patient_service import patient_profile_service, view_profile_service, create_insurance_service, update_insurance_service, view_medical_history_service

router = APIRouter(prefix="/v1/patient", tags=["Manage Patient Profiles"])

@router.post("/profile")
async def create_patient_profile(
    data: PatientProfileCreate,
    request: Request,
):
    
    return await patient_profile_service(data, request)


@router.get("/me/{patient_id}")
async def view_patient_profile(
    patient_id: UUID,
    request: Request,
):
    
    return await view_profile_service(patient_id, request)


@router.post("/insurance")
async def create_insurance(data: InsuranceCreate, request: Request):
    return await create_insurance_service(data, request) 

@router.put("/insurance/{insurance_id}")
async def update_insurance(insurance_id: UUID,  data: UpdateInsurance, request: Request):
    return await update_insurance_service(insurance_id, data, request)


#view medical history
@router.get("/medical-history/{patient_id}")
async def view_medical_history(patient_id: UUID, request: Request):
    return await view_medical_history_service(patient_id, request)