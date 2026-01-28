from datetime import datetime, timedelta, timezone
import token
from fastapi import HTTPException, Request, status
from utils.security import generate_verification_token, verify_password, create_access_token
from services.logs_service import write_log
from utils.email import send_email
from uuid import UUID
from fastapi.responses import JSONResponse



async def user_login_service(user, request: Request):
    try:
        async with request.app.state.pool.acquire() as conn:
            db_user = await conn.fetchrow(
                "SELECT * FROM app_user WHERE email=$1",
                user.email
            )

            # ---- User Not Found ----
            if not db_user:
                raise HTTPException(status_code=401, detail="Invalid email or password")

            # ---- Check if User is Active ----
            if db_user["is_active"] is False:
                raise HTTPException(status_code=403, detail="User account is inactive")

            # ---- Verify Password ----
            if not verify_password(user.password, db_user["password_hash"]):
                raise HTTPException(status_code=401, detail="Invalid email or password")

            # Set request user ID
            request.state.user_id = db_user["id"]

            

            # Generate Token
            token_expires = timedelta(minutes=3600)
            access_token = create_access_token(
                data={"user_id": str(db_user["id"]), "role": db_user["role"]},
                expires_delta=token_expires
            )

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": db_user["id"],
                    "email": db_user["email"],
                    "user_name": db_user["user_name"],
                    "role": db_user["role"],
                    "is_active": db_user["is_active"],
                }
            }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )




async def user_magiclogin_service(user, request: Request, background_tasks):
    try:
        async with request.app.state.pool.acquire() as conn:
            db_user = await conn.fetchrow(
                "SELECT * FROM app_user WHERE email=$1",
                user.email
            )

            # ---- User Not Found ----
            if not db_user:
                raise HTTPException(status_code=401, detail="User Not Found!")

            # ---- Check if User is Active ----
            if db_user["is_active"] is False:
                raise HTTPException(status_code=403, detail="User account is inactive")

            # Set request user ID
            request.state.user_id = db_user["id"]

            # Generate Token
            
            verification_token = generate_verification_token()
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)


            await conn.execute(
            """
            INSERT INTO magiclogin_tokens (token, user_id, expires_at)
            VALUES ($1, $2, $3)
            """,
            verification_token, db_user["id"], expires_at
        )
            
            magiclogin_url = f"{request.base_url}v1/auth/verify-magiclogin?token={verification_token}"

            print ("Magic Login URL:", magiclogin_url)

        body_content = f"""
        <p>Hello <strong>{user.email}</strong>,</p>
        <p>Please click on below link for login:</p>
        <p style="text-align: center;">
            <a href="{magiclogin_url}" class="button">Login with Magic link</a>
        </p>
        <p>If you didn’t send login request, you can safely ignore this email.</p>

        """ 
        background_tasks.add_task(send_email, user.email,"Login with magic link" , body_content)
        #return dict(row)
        #row_serializable = {k: str(v) if isinstance(v, (UUID, datetime)) else v for k, v in row.items()}


        response_content = {
        "type": "success",
        "msg": "Magic link sent on email",
        
        }

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=response_content)

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    

async def verify_magiclogin_service(token, request: Request):
    try:
        
        async with request.app.state.pool.acquire() as conn:

            token_data = await conn.fetchrow(
            """
            SELECT vt.*, u.id as user_id 
            FROM magiclogin_tokens vt
            JOIN app_user u ON vt.user_id = u.id
            WHERE vt.token = $1 AND vt.expires_at > NOW()
            """,
            token
            )
        if not token_data:
            raise HTTPException(status_code=400, detail="Invalid or expired verification token")
        
        async with request.app.state.pool.acquire() as conn:
            
            db_user = await conn.fetchrow(
                    "SELECT * FROM app_user WHERE id=$1",
                    token_data["user_id"]
                )
                # ---- User Not Found ----
            if not db_user:
                    raise HTTPException(status_code=401, detail="User Not Found!")

                # ---- Check if User is Active ----
            if db_user["is_active"] is False:
                    raise HTTPException(status_code=403, detail="User account is inactive")

                # Set request user ID
            request.state.user_id = db_user["id"]
    
            await conn.execute(
                    "DELETE FROM magiclogin_tokens WHERE token = $1",
                    token
                )    

                # Generate Token
            token_expires = timedelta(minutes=15)
            access_token = create_access_token(
            data={"user_id": str(db_user["id"]), "role": db_user["role"]},
            expires_delta=token_expires
                )

            return {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "user": {
                        "id": db_user["id"],
                        "email": db_user["email"],
                        "user_name": db_user["user_name"],
                        "role": db_user["role"],
                        "is_active": db_user["is_active"],
                    }
                }
        

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    

