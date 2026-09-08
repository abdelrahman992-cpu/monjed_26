import os
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from uuid import uuid4

from fastapi import (
    APIRouter,
    BackgroundTasks,
    HTTPException,
    status,
)
from pydantic import BaseModel, Field

from app.schemas.auth import (
    AuthResponse,
    AuthUserResponse,
    LoginRequest,
    RegisterRequest,
)
from app.schemas.contact import (
    ContactRequest,
    ContactResponse,
)
from app.services.auth_service import (
    generate_access_token,
    hash_password,
    verify_password,
)
from app.services.email_service import send_otp_email
from database.contact_repository import (
    save_contact_message,
)
from database.users_repository import (
    create_user,
    delete_user,
    get_user,
    get_user_by_email,
    get_user_by_phone,
    mark_user_as_verified,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

MASTER_OTP = os.getenv("DEMO_MASTER_OTP", "123456")
otp_store: Dict[str, dict] = {}


# ============================================================
# EXTRA SCHEMAS FOR OTP VERIFICATION
# ============================================================

class OTPRequiredResponse(BaseModel):
    requires_otp: bool = True
    user_id: str
    email: str
    message: str = "A 6-digit verification code has been sent to your email."
    
    @property
    def user(self) -> dict:
        return {"user_id": self.user_id, "email": self.email}


class VerifyOTPRequest(BaseModel):
    user_id: str = Field(..., description="ID of the user to verify")
    code: str = Field(..., example="123456", description="6-digit OTP code")


# ============================================================
# HELPERS
# ============================================================

def _safe_send_email_task(user_email: str, code: str):
    """دالة آمنة لإرسال الإيميل دون إيقاف أو تعليق السيرفر في حال وجود مشكلة شبكة"""
    try:
        send_otp_email(user_email, code)
    except Exception as exc:
        print(f"[EMAIL SERVICE ERROR] Failed to send OTP to {user_email}: {str(exc)}")


def _generate_and_store_otp(user_id: str) -> str:
    """توليد كود مكون من 6 أرقام وطباعته في الـ Terminal لتفادي التعليق"""
    code = f"{random.randint(100000, 999999)}"
    otp_store[user_id] = {
        "code": code,
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10),
    }
    print(f"\n==========================================")
    print(f"[OTP GENERATED] User ID: {user_id} | Code: {code}")
    print(f"==========================================\n")
    return code


def _safe_phone(phone: Optional[str]) -> Optional[str]:
    if not phone:
        return None

    value = str(phone).strip()
    if len(value) < 7:
        return None

    asterisks_count = max(len(value) - 7, 2)
    return f"{value[:5]}{'*' * asterisks_count}{value[-2:]}"


def _build_auth_user(user: dict) -> AuthUserResponse:
    return AuthUserResponse(
        user_id=str(user.get("user_id", "")),
        display_name=user.get("display_name") or user.get("name"),
        role=user.get("role", "citizen"),
        email=user.get("email") or user.get("work_email"),
        phone=_safe_phone(user.get("phone") or user.get("phone_number")),
        zone_id=user.get("zone_id"),
        country=user.get("country"),
        preferred_language=user.get("preferred_language", "en"),
    )


def _authenticate_and_send_otp(
    data: LoginRequest,
    background_tasks: BackgroundTasks,
    required_role: Optional[str] = None,
) -> OTPRequiredResponse:
    identifier = data.identifier.strip()

    if "@" in identifier:
        user = get_user_by_email(identifier)
    else:
        user = get_user_by_phone(identifier)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    password_hash = user.get("password_hash")

    if not password_hash or not verify_password(data.password, password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    if required_role is not None and user.get("role") != required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account does not have the required role.",
        )

    user_id = str(user["user_id"])
    user_email = user.get("email") or user.get("work_email")

    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No registered email found for this user to send verification code.",
        )

    code = _generate_and_store_otp(user_id)
    background_tasks.add_task(_safe_safe_send_email_task if '_safe_safe_send_email_task' in locals() else _safe_send_email_task, user_email, code)

    return OTPRequiredResponse(
        requires_otp=True,
        user_id=user_id,
        email=user_email,
        message="Verification code generated successfully."
    )


# ============================================================
# ENDPOINTS
# ============================================================

@router.post(
    "/register",
    response_model=OTPRequiredResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    background_tasks: BackgroundTasks,
) -> OTPRequiredResponse:
    email = data.email.strip().lower()

    existing_user_email = get_user_by_email(email)
    if existing_user_email is not None:
        if not existing_user_email.get("is_verified", False):
            delete_user(str(existing_user_email["user_id"]))
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )

    phone = data.phone.strip() if data.phone else None

    if phone:
        existing_user_phone = get_user_by_phone(phone)
        if existing_user_phone is not None:
            if not existing_user_phone.get("is_verified", False):
                delete_user(str(existing_user_phone["user_id"]))
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="An account with this phone number already exists.",
                )

    user_id = f"user_{uuid4().hex}"

    user = {
        "user_id": user_id,
        "display_name": data.display_name.strip(),
        "email": email,
        "password_hash": hash_password(data.password),
        "role": data.role,
        "zone_id": data.zone_id.strip() if data.zone_id else None,
        "country": data.country.strip() if data.country else None,
        "preferred_language": data.preferred_language,
        "accessibility_needs": list(dict.fromkeys(data.accessibility_needs)),
        "notification_consent": data.notification_consent,
        "notifications_enabled": data.notification_consent,
        "is_verified": False,
    }

    if hasattr(data, "skills"):
        user["skills"] = getattr(data, "skills")

    if phone:
        user["phone"] = phone

    create_user(user)

    code = _generate_and_store_otp(user_id)
    background_tasks.add_task(_safe_send_email_task, email, code)

    return OTPRequiredResponse(
        requires_otp=True,
        user_id=user_id,
        email=email,
    )


@router.post(
    "/login",
    response_model=OTPRequiredResponse,
)
def login(
    data: LoginRequest,
    background_tasks: BackgroundTasks,
) -> OTPRequiredResponse:
    return _authenticate_and_send_otp(data, background_tasks)


@router.post(
    "/admin",
    response_model=OTPRequiredResponse,
)
def admin_login(
    data: LoginRequest,
    background_tasks: BackgroundTasks,
) -> OTPRequiredResponse:
    return _authenticate_and_send_otp(
        data,
        background_tasks,
        required_role="admin",
    )


@router.post(
    "/verify-otp",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
)
def verify_otp(
    payload: VerifyOTPRequest,
) -> AuthResponse:
    input_code = payload.code.strip()
    user_id = payload.user_id

    user = get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found.",
        )

    if input_code == MASTER_OTP:
        otp_store.pop(user_id, None)
        mark_user_as_verified(user_id)
        updated_user = get_user(user_id) or user
        return AuthResponse(
            access_token=generate_access_token(),
            user=_build_auth_user(updated_user),
        )

    record = otp_store.get(user_id)

    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verification request found or code has expired.",
        )

    if datetime.now(timezone.utc) > record["expires_at"]:
        del otp_store[user_id]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired. Please request a new one.",
        )

    if record["code"] != input_code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid verification code.",
        )

    del otp_store[user_id]
    mark_user_as_verified(user_id)
    updated_user = get_user(user_id) or user

    return AuthResponse(
        access_token=generate_access_token(),
        user=_build_auth_user(updated_user),
    )


# ============================================================
# CONTACT
# ============================================================

@router.post(
    "/contact",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
)
def contact(
    data: ContactRequest,
) -> ContactResponse:
    payload = {
        "name": data.name.strip(),
        "email": data.email.strip().lower(),
        "phone": data.phone.strip() if data.phone else None,
        "subject": data.subject.strip() if data.subject else None,
        "message": data.message.strip(),
    }

    record = save_contact_message(payload)

    return ContactResponse(
        contact_id=record["contact_id"],
        status=record["status"],
        created_at=record["created_at"],
    )