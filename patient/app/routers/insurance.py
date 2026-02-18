from fastapi import APIRouter, HTTPException, Request, Depends
from models import InsuranceCreate, UpdateInsurance
from uuid import UUID

from services.insurance_service import create_insurance_service, update_insurance_service, view_insurance_service, delete_insurance_service

router = APIRouter(prefix="/v1/patient/insurance", tags=["Manage Patient Profiles"])


@router.post("")
async def create_insurance(data: InsuranceCreate, request: Request):
    return await create_insurance_service(data, request) 

@router.put("/{insurance_id}")
async def update_insurance(insurance_id: UUID,  data: UpdateInsurance, request: Request):
    return await update_insurance_service(insurance_id, data, request)

@router.get("/{patient_id}")
async def view_insurance(patient_id: UUID, request: Request):
    return await view_insurance_service(patient_id, request)


@router.delete("/{insurance_id}")
async def delete_insurance(insurance_id: UUID, request: Request):
    return await delete_insurance_service(insurance_id, request)