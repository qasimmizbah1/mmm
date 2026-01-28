from datetime import timedelta
from fastapi import HTTPException, Request
from utils.security import verify_password, create_access_token
from services.logs_service import write_log

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

            # -------- Fetch Role-Based Profile --------
            user_profile = None

            if db_user["role"] == "supplier":
                user_profile = await conn.fetchrow(
                    "SELECT * FROM supplier_profile WHERE user_id = $1",
                    db_user["id"]
                )

            elif db_user["role"] == "buyer":
                user_profile = await conn.fetchrow(
                    "SELECT * FROM buyer_profile WHERE user_id = $1",
                    db_user["id"]
                )

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
                    "profile": dict(user_profile) if user_profile else None
                }
            }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

