import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

# SMTP Configuration (Read from Environment Variables for Security)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "monjed.app@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")  # App Password from Google Account


def send_otp_email(to_email: str, code: str) -> bool:
    """
    Send an OTP verification code to the user's email address via Free Gmail SMTP.
    """
    if not SENDER_PASSWORD:
        print("[WARNING] SENDER_PASSWORD is not set. Email was not sent.")
        # Fallback for Development Phase: print to console
        print(f"[DEV ONLY] Verification OTP for {to_email} is: {code}")
        return True

    subject = f"{code} - Your MONJED Verification Code"

    # Clean and professional HTML email template in English
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f6f9; margin: 0; padding: 20px; }}
            .card {{ max-width: 480px; margin: 0 auto; background: #ffffff; border-radius: 12px; padding: 32px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; }}
            .brand {{ font-size: 24px; font-weight: bold; color: #0f172a; margin-bottom: 20px; letter-spacing: -0.5px; }}
            .code-box {{ background-color: #f1f5f9; border: 2px dashed #0284c7; border-radius: 8px; padding: 16px; font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #0284c7; margin: 24px 0; }}
            .text {{ font-size: 15px; color: #334155; line-height: 1.6; margin: 0 0 16px 0; }}
            .footer {{ font-size: 12px; color: #94a3b8; margin-top: 28px; line-height: 1.5; border-top: 1px solid #e2e8f0; padding-top: 16px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="brand">🚨 MONJED Platform</div>
            <p class="text">Welcome! Use the verification code below to complete your authentication process:</p>
            <div class="code-box">{code}</div>
            <p class="text">This code is valid for <strong>10 minutes</strong>. For security reasons, please do not share this code with anyone.</p>
            <div class="footer">If you did not request this verification code, please ignore this email.<br>© MONJED AI Platform. All rights reserved.</div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"MONJED AI <{SENDER_EMAIL}>"
    msg["To"] = to_email

    msg.attach(MIMEText(f"Your verification code is: {code}", "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send OTP email to {to_email}: {str(e)}")
        return False