from fastapi import APIRouter, HTTPException, Request, Depends, Response
from uuid import UUID
from deps import require_admin
from services.logs_service import write_log

async def view_user_service(user_role,request: Request):
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, email, role, is_active, user_name FROM app_user WHERE role = $1 order by created_at DESC", user_role.role)
        return [dict(row) for row in rows]

async def get_user_service(user_id, request: Request):
    async with request.app.state.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, email, role, is_active,user_name FROM app_user WHERE id = $1",
            str(user_id)  # convert UUID to string if your DB stores as text
        )
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(row)
    
async def delete_user_service(user_id, request: Request):
    async with request.app.state.pool.acquire() as conn:
        async with conn.transaction():
           
            result = await conn.execute(
                "DELETE FROM app_user WHERE id = $1",
                str(user_id)
            )

            if result.endswith("0"):
                raise HTTPException(status_code=404, detail="User not found")
            
        await write_log(
                request=request,
                action="DELETE_USER",
                level="INFO",
                user_id='',
                meta={"email": '', "role": 'admin'}
            )    

    return {"message": "User deleted successfully"}



async def update_user_service(user_id, user_update, request: Request):
    async with request.app.state.pool.acquire() as conn:
        async with conn.transaction():

            # Check if user exists
            existing_user = await conn.fetchrow(
                "SELECT * FROM app_user WHERE id=$1", str(user_id)
            )
            if not existing_user:
                raise HTTPException(status_code=404, detail="User not found")

            # ---------- Update app_user ----------
            app_user_update_fields = []
            app_user_values = []
            idx = 1

            if user_update.is_active is not None:
                app_user_update_fields.append(f"is_active = ${idx}")
                app_user_values.append(user_update.is_active)
                idx += 1

            if user_update.user_name is not None:
                app_user_update_fields.append(f"user_name = ${idx}")
                app_user_values.append(user_update.user_name)
                idx += 1

            if user_update.phone_number is not None:
                app_user_update_fields.append(f"phone_number = ${idx}")
                app_user_values.append(user_update.phone_number)
                idx += 1

            updated_user = None
            
            if app_user_update_fields:
                app_user_values.append(str(user_id))
                query = f"""
                    UPDATE app_user 
                    SET {', '.join(app_user_update_fields)} 
                    WHERE id=${idx} 
                    RETURNING *
                """
                updated_user = await conn.fetchrow(query, *app_user_values)
            else:
                updated_user = existing_user  # no changes to app_user

            # ---------- Update buyer_profile ----------
            idx = 1


            

            await write_log(
                request=request,
                action="UPDATE_PATIENT",
                level="INFO",
                user_id='',
                meta={"email": '', "role": 'admin'}
            )

            # ---------- Return merged response ----------
            return {
                "user": dict(updated_user),
            }


    
