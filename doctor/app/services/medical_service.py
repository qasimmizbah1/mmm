from unittest import result
from fastapi import APIRouter, HTTPException, Request, Depends, Response
from uuid import UUID

#add medical history record       
async def medical_history_service(data, request: Request):
    async with request.app.state.pool.acquire() as conn:
        try:
            await conn.execute("""
            INSERT INTO medical_history (
                patient_id,
                doctor_id,
                diagnosis,
                treatment_plan,
                medications,
                notes
            )
            VALUES ($1,$2,$3,$4,$5,$6)
        """,
        data.patient_id,
        data.doctor_id,
        data.diagnosis,
        data.treatment_plan,
        data.medications,
        data.notes
        )
            return {"status_code": 200, "message": "Medical history record created successfully."}

        except Exception as e:
             return {"status_code": 500, "message": f"Failed to create medical history record: {str(e)}"}
        

#edit history record
async def update_history_service(history_id, data, request: Request):
    async with request.app.state.pool.acquire() as conn:
        try:

            check_history = await conn.fetchrow("SELECT * FROM medical_history WHERE id = $1", history_id)
            if not check_history:
                return {"status_code": 404, "message": "Medical history record not found."}

            await conn.execute("""
            UPDATE medical_history
            SET
                diagnosis      = COALESCE($2, diagnosis),
                treatment_plan = COALESCE($3, treatment_plan),
                medications    = COALESCE($4, medications),
                notes          = COALESCE($5, notes),
                updated_at     = now()
            WHERE id = $1
        """,
        history_id,
        data.diagnosis,
        data.treatment_plan,
        data.medications,
        data.notes
        )
            return {"status_code": 200, "message": "Medical history record updated successfully."}

        except Exception as e:
             return {"status_code": 500, "message": f"Failed to update medical history record: {str(e)}"}
        


#delete history record
async def delete_history_service(history_id, request: Request):
    async with request.app.state.pool.acquire() as conn:
        try:

            check_history = await conn.fetchrow("SELECT * FROM medical_history WHERE id = $1", history_id)
            if not check_history:
                return {"status_code": 404, "message": "Medical history record not found."}

            await conn.execute("DELETE FROM medical_history WHERE id = $1", history_id)
            return {"status_code": 200, "message": "Medical history record deleted successfully."}

        except Exception as e:
             return {"status_code": 500, "message": f"Failed to delete medical history record: {str(e)}"}