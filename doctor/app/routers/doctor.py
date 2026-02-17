from fastapi import APIRouter, HTTPException, Request, Depends
from models import UserRole, ReferralCreate, DoctorProfileCreate, MedicalHistory, updateMedicalHistory
from uuid import UUID
from services.doctor_service import view_user_service, create_referral_service, view_referral_service, doctor_profile_service, viewall_referrals_service, view_profile_service

router = APIRouter(prefix="/v1/doctor", tags=["Manage Doctors"])


@router.post("/user")
async def view_patient(user_role:UserRole, request: Request):
    return await view_user_service(user_role, request)




@router.post("/referrals")
async def create_referral(
    data: ReferralCreate,
    request: Request
):
    return await create_referral_service(data, request)

@router.get("/referrals/{id}")
async def view_referral(
    id: UUID, request: Request
):
    return await view_referral_service(id, request)


@router.get("/allreferrals/{doctor_id}")
async def view_all_referrals(doctor_id: UUID, request: Request):
    return await viewall_referrals_service(doctor_id, request)
    

@router.post("/profile")
async def create_doctor_profile(
    data: DoctorProfileCreate,
    request: Request,
):
    
    return await doctor_profile_service(data, request)


@router.get("/profile/me/{doctor_id}")
async def view_doctor_profile(
    doctor_id: UUID,
    request: Request,
):
    
    return await view_profile_service(doctor_id, request)

