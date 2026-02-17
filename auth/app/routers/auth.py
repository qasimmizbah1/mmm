from fastapi import APIRouter, Request, BackgroundTasks, Body, Depends
from models import UserRegister, UserLogin, UserOut, ForgotPasswordRequest, ResetPasswordRequest, MagicUserLogin, TokenData
from services.login_service import user_login_service, user_magiclogin_service, verify_magiclogin_service, refresh_token_service, verify_token_service
from services.register_service import user_register_service, user_verify_service, user_resend_verification_service
from services.password_service import user_change_password_service, forgot_password_service, reset_password_service
from deps import require_login
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")


router = APIRouter(prefix="/v1/auth", tags=["Auth"])

# Endpoint to Register
@router.post("/register", response_model=UserOut)
async def register_user(user: UserRegister, request: Request, background_tasks: BackgroundTasks):
    return await user_register_service(user, request, background_tasks)


@router.get("/verify-email")
async def verify_email(token: str, request: Request):
    return await user_verify_service(token, request)    


@router.post("/resend-verification")
async def resend_verification(email: str, request: Request, background_tasks: BackgroundTasks):
    return await user_resend_verification_service(email, request, background_tasks)
    
    
# Endpoint to Login
@router.post("/login")
async def login_user(user: UserLogin, request: Request):
    return await user_login_service(user, request)
    
@router.post("/magiclogin")
async def login_user(user: MagicUserLogin, request: Request, background_tasks: BackgroundTasks):
    return await user_magiclogin_service(user, request, background_tasks)

@router.get("/verify-magiclogin")
async def verify_email(token: str, request: Request):
    return await verify_magiclogin_service(token, request)


# Endpoint to change password
@router.post("/change-password")
async def change_password(
    email: str = Body(..., embed=True),   # or use JWT later for authenticated user
    old_password: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True),
    confirm_new_password: str = Body(..., embed=True),
    request: Request = None,
    payload: dict = Depends(require_login), background_tasks: BackgroundTasks = None
):
    return await user_change_password_service(
        email, old_password, new_password, confirm_new_password, request, background_tasks
    )   


# ---- Forgot password ----
@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, request: Request, background_tasks: BackgroundTasks):
    return await forgot_password_service(data.email, request, background_tasks)


# ---- Reset password ----
@router.post("/reset-password",)
async def reset_password(data: ResetPasswordRequest, request: Request, background_tasks: BackgroundTasks):
   return await reset_password_service(data, request, background_tasks)


@router.post("/email-send")
#@rate_limit(limit=5, seconds=60)
async def send_email(request: Request):
    try:
        receiver_email = "qasimmizbah@gmail.com"  # <-- change this to your test email
        subject = "Test Email from FastAPI"
        body = "Hello! This is a test email sent from FastAPI using Gmail SMTP."

        # Create the email message
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = receiver_email

        # Connect to Gmail SMTP server and send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # enable security
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())

        return {"message": f"Email sent successfully to {receiver_email}"}

    except Exception as e:
        return {"error": str(e)}
    


@router.post("/refresh-token")
async def refresh_token(refresh_token: TokenData, request: Request):
    return await refresh_token_service(refresh_token, request)



@router.post("/verify-token")
async def verify_token(token: TokenData, request: Request):
    return await verify_token_service(token, request)