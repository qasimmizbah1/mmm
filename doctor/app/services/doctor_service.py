from fastapi import APIRouter, HTTPException, Request, Depends, Response
from uuid import UUID


async def view_user_service(user_role,request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, email, role, is_active, user_name FROM app_user WHERE role = $1 order by created_at DESC", user_role.role)
        return [dict(row) for row in rows]

async def create_referral_service(data, request: Request):
    
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
        data.doctor_id,
        data.patient_id,
        data.therapist_id,
        data.urgency_level,
        data.preferred_modality,
        data.clinical_presentation,
        data.chief_complaint,
        data.additional_requirements
        )

        return {
            "message": "Referral created successfully",
            "referral_id": referral_id
        }


    
