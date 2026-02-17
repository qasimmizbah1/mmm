from fastapi import APIRouter, HTTPException, Request, Depends
from models import MedicalHistory, updateMedicalHistory
from uuid import UUID

from services.medical_service import medical_history_service, update_history_service, delete_history_service

router = APIRouter(prefix="/v1/medical-history", tags=["Manage Medical History"])



@router.post("")
async def create_medical_history(
    data: MedicalHistory,
    request: Request,
):
    
    return await medical_history_service(data, request)


@router.put("/{history_id}")
async def update_medical_history(
    history_id: UUID,
    data: updateMedicalHistory,
    request: Request,
):
    
    return await update_history_service(history_id, data, request)


@router.delete("/{history_id}")
async def delete_medical_history(history_id: UUID, request: Request):
    return await delete_history_service(history_id, request)