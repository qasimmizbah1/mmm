from fastapi import APIRouter, HTTPException, Request, Depends
from models import UserRole, ReferralCreate, DoctorProfileCreate
from uuid import UUID

from services.doctor_service import view_user_service, create_referral_service

router = APIRouter(prefix="/v1/doctor", tags=["Manage Users"])


@router.post("/user")
async def view_patient(user_role:UserRole, request: Request):
    return await view_user_service(user_role, request)




@router.post("/referrals")
async def create_referral(
    data: ReferralCreate,
    request: Request
):
    return await create_referral_service(data, request)


@router.get("/viewreferrals/{doctor_id}")
async def therapist_referrals(doctor_id: UUID, request: Request):
    async with request.app.state.pool.acquire() as conn:
       rows = await conn.fetch("""
    SELECT
        r.*,
        patient.user_name   AS patient_name,
        therapist.user_name AS therapist_name,
        referrer.user_name  AS referred_by_name
    FROM referrals r
    JOIN app_user patient   ON patient.id   = r.patient_id
    JOIN app_user therapist ON therapist.id = r.therapist_id
    LEFT JOIN app_user referrer ON referrer.id = r.doctor_id
    WHERE r.doctor_id = $1
""", doctor_id)

    return [dict(row) for row in rows]
    

@router.post("/doctor/profile")
async def create_doctor_profile(
    data: DoctorProfileCreate,
    request: Request,
):

    async with request.app.state.pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO doctor_profile (
                doctor_id,
                full_name,
                license_number,
                registration,
                clinic_name,
                medical_field,
                address,
                phone,
                gender,
                dob
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
        """,
        data.doctor_id,
        data.full_name,
        data.license_number,
        data.registration,
        data.clinic_name,
        data.medical_field,
        data.address,
        data.phone,
        data.gender,
        data.dob
        )

        return {"message": "Doctor profile created successfully"}


@router.put("/doctor/profile/")
async def update_doctor_profile(
    data: DoctorProfileCreate,
    request: Request,
):
    async with request.app.state.pool.acquire() as conn:
        await conn.execute("""
            UPDATE doctor_profile
            SET
                full_name = $1,
                license_number = $2,
                registration = $3,
                clinic_name = $4,
                medical_field = $5,
                address = $6,
                phone = $7,
                gender = $8,
                dob = $9,
                updated_at = now()
            WHERE doctor_id = $10
        """,
        data.full_name,
        data.license_number,
        data.registration,
        data.clinic_name,
        data.medical_field,
        data.address,
        data.phone,
        data.gender,
        data.dob,
        data.doctor_id
        )

        return {"message": "Doctor profile updated successfully"}
