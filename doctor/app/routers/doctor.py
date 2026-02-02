from fastapi import APIRouter, HTTPException, Request, Depends
from models import UserRole
from uuid import UUID

from services.users_service import view_user_service

router = APIRouter(prefix="/v1/admin/manage-users", tags=["Manage Users"])


@router.post("/user")
async def view_patient(user_role:UserRole, request: Request):
    return await view_user_service(user_role, request)