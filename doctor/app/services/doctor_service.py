from fastapi import APIRouter, HTTPException, Request, Depends, Response
from uuid import UUID


async def view_user_service(user_role,request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, email, role, is_active, user_name FROM app_user WHERE role = $1 order by created_at DESC", user_role.role)
        return [dict(row) for row in rows]

async def create_referral_service(payload, user, request: Request):
    if user["role"] != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can create referrals")

    async with request.app.state.pool.acquire() as conn:
        referral_id = await conn.fetchval("""
            INSERT INTO referrals (
                doctor_id,
                patient_id,
                therapist_id,
                urgency_level,
                preferred_modality,
                clinical_presentation,
                chief_complaint,
                additional_requirements,
                status
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,'pending')
            RETURNING id
        """,
        user["id"],
        payload.patient_id,
        payload.therapist_id,
        payload.urgency_level,
        payload.preferred_modality,
        payload.clinical_presentation,
        payload.chief_complaint,
        payload.additional_requirements
        )

        return {
            "message": "Referral created successfully",
            "referral_id": referral_id
        }


    
