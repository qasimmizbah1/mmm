import os
from unittest import result
from fastapi import APIRouter, HTTPException, Request, Depends, Response, UploadFile
from uuid import UUID
from datetime import datetime
import uuid

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

async def viewall_referrals_service(doctor_id, request: Request):
    
    try:
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

            result = []
            for row in rows:
                row_dict = dict(row)
                row_dict.pop("doctor_id", None)  # Remove doctor_id if it exists
                result.append(row_dict)

            return {"status_code": 200, "data": result}
       
    except Exception as e:
           return {"status_code": 500, "message": f"Failed to retrieve referrals: {str(e)}"}
    
async def view_referral_service(id, request: Request):
    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT
                r.*,
                patient.user_name   AS patient_name,
                therapist.user_name AS therapist_name,
                referrer.user_name  AS referred_by_name
            FROM referrals r
            JOIN app_user patient   ON patient.id   = r.patient_id
            JOIN app_user therapist ON therapist.id = r.therapist_id
            LEFT JOIN app_user referrer ON referrer.id = r.doctor_id
            WHERE r.id = $1
        """, id)

        if row:
            row_dict = dict(row)
            row_dict.pop("doctor_id", None)  # Remove doctor_id if it exists
            return {"status_code": 200, "data": row_dict}
        else:
            return {"status_code": 404, "message": "Referral not found"}


async def doctor_profile_service(request: Request, doctor_id: str, full_name: str, license_number: str, registration: str, clinic_name: str, medical_field: str, address: str, phone: str, gender: str, dob: str, profile_image: UploadFile = None):
      
      async with request.app.state.pool.acquire() as conn:
        try:

            if not dob:
                dob_value = None
            else:
                dob_value = datetime.strptime(dob, "%Y-%m-%d").date()

            old_record = await conn.fetchrow(
                "SELECT profile_image FROM doctor_profile WHERE doctor_id=$1",
                doctor_id
            )
            old_image_path = old_record["profile_image"] if old_record else None

            image_path = old_image_path

            if profile_image:
                BASE_DIR = os.path.dirname(os.path.dirname(
                os.path.dirname( os.path.dirname(os.path.abspath(__file__)))
                ))

                upload_dir = os.path.join(BASE_DIR, "public_files/images")
                print("Upload directory:", upload_dir)
                os.makedirs(upload_dir, exist_ok=True)

                if old_image_path and os.path.exists(old_image_path):
                    os.remove(old_image_path)

                file_ext = profile_image.filename.split(".")[-1]
                filename = f"{uuid.uuid4()}.{file_ext}"


                image_path = f"{upload_dir}/{filename}"

                with open(image_path, "wb") as buffer:
                    buffer.write(await profile_image.read())
                    
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
                dob,
                profile_image
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
            ON CONFLICT (doctor_id) 
            DO UPDATE SET
                full_name       = COALESCE(EXCLUDED.full_name, doctor_profile.full_name),
                license_number  = COALESCE(EXCLUDED.license_number, doctor_profile.license_number),
                registration    = COALESCE(EXCLUDED.registration, doctor_profile.registration),
                clinic_name     = COALESCE(EXCLUDED.clinic_name, doctor_profile.clinic_name),
                medical_field   = COALESCE(EXCLUDED.medical_field, doctor_profile.medical_field),
                address         = COALESCE(EXCLUDED.address, doctor_profile.address),
                phone           = COALESCE(EXCLUDED.phone, doctor_profile.phone),
                gender          = COALESCE(EXCLUDED.gender, doctor_profile.gender),
                dob             = COALESCE(EXCLUDED.dob, doctor_profile.dob),
                profile_image   = COALESCE(EXCLUDED.profile_image, doctor_profile.profile_image)
        """,
        doctor_id,
        full_name,
        license_number,
        registration,
        clinic_name,
        medical_field,
        address,
        phone,
        gender,
        dob_value,
        filename if profile_image else None
        )
            return {"status_code": 200, "message": "Doctor profile updated successfully."}

        except Exception as e:
             return {"status_code": 500, "message": f"Failed to update doctor profile: {str(e)}"}
        

async def view_profile_service(doctor_id, request: Request):
    async with request.app.state.pool.acquire() as conn:
        
        row = await conn.fetchrow("""
            SELECT
                dp.*,
                au.user_name AS doctor_name,
                au.email     AS doctor_email
            FROM doctor_profile dp
            JOIN app_user au ON au.id = dp.doctor_id
            WHERE au.id = $1
        """, doctor_id)

        if row:
            return {"status_code": 200, "data": dict(row)}
        else:
            return {"status_code": 404, "message": "Doctor profile not found"}
        
