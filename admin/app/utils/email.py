from datetime import datetime
from email.mime.text import MIMEText
import os
import smtplib
from dotenv import load_dotenv



load_dotenv()
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")


def build_email_template(subject: str, body_content: str) -> str:
    """
    Returns a full HTML email with header and footer.
    body_content is the variable part (custom message).
    """
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>{subject}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Roboto, Arial, sans-serif;
                background-color: #f4f4f7;
                margin: 0;
                padding: 0;
            }}
            .email-container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #ffffff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            }}
            .header {{
                background-color: #0b5ed7;
                color: #ffffff;
                text-align: center;
                padding: 20px;
                font-size: 24px;
                font-weight: bold;
            }}
            .content {{
                padding: 30px;
                color: #333333;
                line-height: 1.6;
                font-size: 16px;
            }}
            .footer {{
                background-color: #f0f0f0;
                text-align: center;
                color: #888888;
                padding: 15px;
                font-size: 13px;
            }}
            a.button {{
                display: inline-block;
                background-color: #0b5ed7;
                color: white;
                text-decoration: none;
                padding: 12px 24px;
                border-radius: 5px;
                margin-top: 20px;
            }}
            a.button:hover {{
                background-color: #084298;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                AutoPartsXchange
            </div>
            <div class="content">
                {body_content}
            </div>
            <div class="footer">
                &copy; {datetime.utcnow().year} AutoPartsXchange. All rights reserved.<br>
                Please do not reply to this email.
            </div>
        </div>
    </body>
    </html>
    """


async def send_email(email: str,subject, body_content: str):

    html_content = build_email_template(subject, body_content)
    msg = MIMEText(html_content, "html")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, email, msg.as_string())
        print(f"✅ Email sent to {email}")
    except Exception as e:
        print(f"❌ Failed to send email to {email}: {e}")
    
    