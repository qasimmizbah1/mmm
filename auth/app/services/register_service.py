from datetime import timedelta, datetime
from fastapi import HTTPException, Request, status
from utils.security import hash_password, generate_verification_token 
from utils.email import send_email
from fastapi.responses import JSONResponse
from uuid import UUID


async def user_register_service(user, request: Request, background_tasks):
    async with request.app.state.pool.acquire() as conn:
        # check if user already exists
        exists = await conn.fetchrow("SELECT 1 FROM app_user WHERE email=$1", user.email)
        if exists:
           raise HTTPException(
                    status_code=400,
                    detail=[
                        {
                            "type": "error",
                            "msg": "Email already registered"
                       
                        }
                    ]
                )

        # hash password
        hashed_password = hash_password(user.password)

        # insert new user
        row = await conn.fetchrow(
            """
            INSERT INTO app_user (email, password_hash, role, is_active, user_name, phone_number)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id::text, email, role, is_active, user_name, phone_number, created_at
            """,
            user.email, hashed_password, user.role, False, user.name, user.phone
        )
        user_id = row["id"]

        
        # Generate verification token
        verification_token = generate_verification_token()
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        # Store verification token
        await conn.execute(
            """
            INSERT INTO verification_tokens (token, user_id, expires_at)
            VALUES ($1, $2, $3)
            """,
            verification_token, user_id, expires_at
        )
        
        # Send verification email in background
        verification_url = f"{request.base_url}v1/auth/verify-email?token={verification_token}"

        body_content = f"""
        <p>Hello <strong>{user.email}</strong>,</p>
        <p>Thank you for registering with us! Please verify your email address by clicking the button below:</p>
        <p style="text-align: center;">
            <a href="{verification_url}" class="button">Verify Email</a>
        </p>
        <p>If you didn’t create an account, you can safely ignore this email.</p>

        """ 
        background_tasks.add_task(send_email, user.email,"Verify Your Email" , body_content)
        #return dict(row)
        row_serializable = {k: str(v) if isinstance(v, (UUID, datetime)) else v for k, v in row.items()}


        response_content = {
        "type": "success",
        "msg": "User registered successfully",
        "data": row_serializable
        }

        return JSONResponse(status_code=status.HTTP_201_CREATED, content=response_content)
    
async def user_verify_service(token, request: Request):
    async with request.app.state.pool.acquire() as conn:
        # Check if token exists and is valid
        token_data = await conn.fetchrow(
            """
            SELECT vt.*, u.id as user_id, u.email 
            FROM verification_tokens vt
            JOIN app_user u ON vt.user_id = u.id
            WHERE vt.token = $1 AND vt.expires_at > NOW()
            """,
            token
        )
        
        if not token_data:
            raise HTTPException(status_code=400, detail="Invalid or expired verification token")
        
        # Activate user
        await conn.execute(
            "UPDATE app_user SET is_active = TRUE WHERE id = $1",
            token_data["user_id"]
        )
        
        # Delete used token
        await conn.execute(
            "DELETE FROM verification_tokens WHERE token = $1",
            token
        )
        
        return {"message": "Email verified successfully! You can now login."}
    

async def user_resend_verification_service(email, request: Request, background_tasks):
    async with request.app.state.pool.acquire() as conn:
        # Check if user exists and is not verified
        user = await conn.fetchrow(
            "SELECT id, is_active FROM app_user WHERE email = $1",
            email
        )
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user["is_active"]:
            raise HTTPException(status_code=400, detail="Email already verified")
        
        # Delete any existing tokens
        await conn.execute(
            "DELETE FROM verification_tokens WHERE user_id = $1",
            user["id"]
        )
        
        # Generate new token
        verification_token = generate_verification_token()
        expires_at = datetime.utcnow() + timedelta(hours=24)
        send_verification_email = ""
        await conn.execute(
            "INSERT INTO verification_tokens (token, user_id, expires_at) VALUES ($1, $2, $3)",
            verification_token, user["id"], expires_at
        )
        
        # Resend email

        verification_url = f"{request.base_url}v1/auth/verify-email?token={verification_token}"

        body_content = f"""
        <p>Hello <strong>{email}</strong>,</p>
        <p>Thank you for registering with us! Please verify your email address by clicking the button below:</p>
        <p style="text-align: center;">
            <a href="{verification_url}" class="button">Verify Email</a>
        </p>
        <p>If you didn’t create an account, you can safely ignore this email.</p>
         """
        
        background_tasks.add_task(send_email, email,"Verify Your Email", body_content)

        

        # background_tasks.add_task(send_verification_email, user.email, verification_token, request)
        
        return {"message": "Verification email sent successfully"}
    



    
