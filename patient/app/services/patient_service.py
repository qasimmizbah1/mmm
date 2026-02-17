from unittest import result
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
    



async def patient_profile_service(data, request: Request):
      
      async with request.app.state.pool.acquire() as conn:
        try:
            await conn.execute("""
            INSERT INTO patient_profile (
                patient_id,
                phone,
                gender,
                dob
            )
            VALUES ($1,$2,$3,$4)
            ON CONFLICT (patient_id) 
            DO UPDATE SET
                phone           = COALESCE(EXCLUDED.phone, patient_profile.phone),
                gender          = COALESCE(EXCLUDED.gender, patient_profile.gender),
                dob             = COALESCE(EXCLUDED.dob, patient_profile.dob)
        """,
        data.patient_id,
        data.phone,
        data.gender,
        data.dob
        )
            return {"status": True, "message": "Patient profile updated successfully."}
        except Exception as e:
             return {"status": False, "message": f"Failed to update patient profile: {str(e)}"}
        

async def view_profile_service(patient_id, request: Request):
    async with request.app.state.pool.acquire() as conn:
        
        row = await conn.fetchrow("""
            SELECT
                dp.*,
                au.user_name AS patient_name,
                au.email     AS patient_email
            FROM patient_profile dp
            JOIN app_user au ON au.id = dp.patient_id
            WHERE au.id = $1
        """, patient_id)

        if row:
            return {"status": True, "data": dict(row)}
        else:
            return {"status": False, "message": "Patient profile not found"}
        


async def create_insurance_service(data, request: Request):
    async with request.app.state.pool.acquire() as conn:
        try:
            
            check_patient = await conn.fetchval("SELECT id FROM app_user WHERE id = $1 AND role = 'patient'", data.patient_id)

            if not check_patient:
                return {"status": False, "message": "Invalid patient ID. No such patient exists."}

            await conn.execute("""
            INSERT INTO insurance (
                patient_id,
                insurance_name,
                policy_number,
                coverage_details,
                notes
            )
            VALUES ($1,$2,$3,$4,$5)
        """,
        data.patient_id,
        data.insurance_name,
        data.policy_number,
        data.coverage_details,
        data.notes
        )
            return {"status": True, "message": "Insurance information added successfully."}
        except Exception as e:
             return {"status": False, "message": f"Failed to add insurance information: {str(e)}"}
        

async def update_insurance_service(insurance_id, data, request: Request):
    async with request.app.state.pool.acquire() as conn:
        try:
            await conn.execute("""
            UPDATE insurance SET
                insurance_name  = COALESCE($1, insurance_name),
                policy_number   = COALESCE($2, policy_number),
                coverage_details= COALESCE($3, coverage_details),
                notes           = COALESCE($4, notes),
                updated_at      = now()
            WHERE id = $5
        """,
        data.insurance_name,
        data.policy_number,
        data.coverage_details,
        data.notes,
        insurance_id
        )
            return {"status": True, "message": "Insurance information updated successfully."}
        except Exception as e:
             return {"status": False, "message": f"Failed to update insurance information: {str(e)}"}
        


#view medical history
async def view_medical_history_service(patient_id, request: Request):
    async with request.app.state.pool.acquire() as conn:
        try:
            rows = await conn.fetch("""
            SELECT
                mh.*,
                au.user_name AS patient_name
            FROM medical_history mh
            JOIN app_user au ON au.id = mh.patient_id
            WHERE au.id = $1
        """, patient_id)

            if rows:
                return {"status": True, "data": [dict(row) for row in rows]}
            else:
                return {"status": False, "message": "No medical history found for this patient."}
        except Exception as e:
             return {"status": False, "message": f"Failed to retrieve medical history: {str(e)}"}