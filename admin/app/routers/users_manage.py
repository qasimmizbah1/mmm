from fastapi import APIRouter, HTTPException, Request, Depends
from models import PatientUpdate, UserRole
from uuid import UUID
from deps import require_admin
from services.users_service import view_user_service, get_user_service, delete_user_service, update_user_service

router = APIRouter(prefix="/v1/admin/manage-users", tags=["Manage Users"])


@router.post("/user")
async def view_patient(user_role:UserRole, request: Request):
    return await view_user_service(user_role, request)

@router.get("/user/user_id")
async def view_patient_by_id(user_id, request: Request):
    return await get_user_service(user_id, request)


@router.delete("/user/{user_id}", status_code=200)
async def delete_patient(user_id: UUID, request: Request):
    return await delete_user_service(user_id, request)


@router.patch("/user/{user_id}", response_model=dict)
async def update_patient(user_id: UUID, patient_update:PatientUpdate, request: Request):
    return await update_user_service(user_id, patient_update, request)
