from unittest import result
from fastapi import APIRouter, HTTPException, Request, Depends, Response
from uuid import UUID

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
        


async def view_insurance_service(patient_id, request: Request):
    async with request.app.state.pool.acquire() as conn:
        
        rows = await conn.fetch("""
            SELECT
                i.*,
                au.user_name AS patient_name
            FROM insurance i
            JOIN app_user au ON au.id = i.patient_id
            WHERE i.patient_id = $1
        """, patient_id)

        if rows:
            return {"status": True, "data": [dict(row) for row in rows]}
        else:
            return {"status": False, "message": "No insurance information found for this patient."}
        


async def delete_insurance_service(insurance_id, request: Request):
    async with request.app.state.pool.acquire() as conn:
        try:
            await conn.execute("DELETE FROM insurance WHERE id = $1", insurance_id)
            return {"status": True, "message": "Insurance information deleted successfully."}
        except Exception as e:
             return {"status": False, "message": f"Failed to delete insurance information: {str(e)}"}