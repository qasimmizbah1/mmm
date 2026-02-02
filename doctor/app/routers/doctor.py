from fastapi import APIRouter, HTTPException, Request, Depends
from models import UserRole
from uuid import UUID

from services.users_service import view_user_service, create_referral_service

router = APIRouter(prefix="/v1/doctor", tags=["Manage Users"])


@router.post("/user")
async def view_patient(user_role:UserRole, request: Request):
    return await view_user_service(user_role, request)




@router.post("/referrals")
async def create_referral(
    payload: ReferralCreate,
    request: Request,
    user=Depends(get_current_user)
):
    return await create_referral_service(payload, user, request)


@router.get("/therapist/referrals")
async def therapist_referrals(request: Request, user=Depends(get_current_user)):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT r.*, u.user_name AS patient_name
            FROM referrals r
            JOIN app_user u ON u.id = r.patient_id
            WHERE r.therapist_id = $1
        """, user["id"])

        return [dict(row) for row in rows]
    

@router.get("/patient/referrals")
async def patient_referrals(request: Request, user=Depends(get_current_user)):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT r.*, t.user_name AS therapist_name
            FROM referrals r
            JOIN app_user t ON t.id = r.therapist_id
            WHERE r.patient_id = $1
        """, user["id"])

        return [dict(row) for row in rows]
