from fastapi import APIRouter, HTTPException, Request, Depends
from models import UserRequest, BuyerUpdate, SupplierUpdate
from uuid import UUID
from deps import require_admin
from services.users_service import view_patient_service, view_supplier_service, get_patient_service, get_user_sup_service, delete_patient_service,  delete_supplier_service, update_patient_service, update_supplier_service

router = APIRouter(prefix="/v1/admin/manage-users", tags=["Manage Users"])


@router.get("/patient")
async def view_patient(request: Request):
    return await view_patient_service(request)

@router.get("/patient/user_id")
async def view_patient_by_id(user_id, request: Request):
    return await get_patient_service(user_id, request)


@router.delete("/patient/{user_id}", status_code=200)
async def delete_patient(user_id: UUID, request: Request):
    return await delete_patient_service(user_id, request)


@router.patch("/patient/{user_id}", response_model=dict)
async def update_patient(user_id: UUID, user_update: BuyerUpdate, request: Request):
    return await update_patient_service(user_id, user_update, request)




@router.get("/referral")
async def view_supplier_profiles(request: Request):
    return await view_supplier_service(request)

@router.get("/referral/user_id")
async def view_supplier_profiles_by_id(user_id, request: Request):
    return await get_user_sup_service(user_id, request)

@router.delete("/referral/{user_id}", status_code=200 , dependencies=[Depends(require_admin)])
async def delete_user(user_id: UUID, request: Request):
    return await delete_supplier_service(user_id, request)

@router.patch("/referral/{user_id}", response_model=dict, dependencies=[Depends(require_admin)])
async def update_supplier(user_id: UUID, supplier_update: SupplierUpdate, request: Request):
    return await update_supplier_service(user_id, supplier_update, request)




@router.get("/therapist")
async def view_buyer_profiles(request: Request):
    return await view_buyer_service(request)

@router.get("/therapist/user_id")
async def view_buyer_profiles_by_id(user_id, request: Request):
    return await get_user_buyer_service(user_id, request)

@router.delete("/therapist/{user_id}", status_code=200 , dependencies=[Depends(require_admin)])
async def delete_user(user_id: UUID, request: Request):
    return await delete_supplier_service(user_id, request)

@router.patch("/therapist/{user_id}", response_model=dict, dependencies=[Depends(require_admin)])
async def update_supplier(user_id: UUID, supplier_update: SupplierUpdate, request: Request):
    return await update_supplier_service(user_id, supplier_update, request)