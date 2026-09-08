from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator

# ============================================================
# TYPES
# ============================================================

SupportedLanguage = Literal[
    "en",
    "ar",
    "sw",
    "fr",
]

AccessibilityNeed = Literal[
    "mobility",
    "visual",
    "hearing",
    "cognitive",
]


# ============================================================
# HELPERS
# ============================================================

def _normalize_optional_phone(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        return value
    cleaned = (
        value.strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )
    if not cleaned:
        return None
    if not cleaned.startswith("+") and cleaned.isdigit():
        cleaned = f"+{cleaned}"
    return cleaned


# ============================================================
# RESPONSES & SCHEMAS
# ============================================================

class UserProfileResponse(BaseModel):
    user_id: str
    display_name: Optional[str] = None
    role: Optional[str] = None
    role_title: Optional[str] = None
    organization: Optional[str] = None
    work_email: Optional[str] = None

    # Frontend receives only a masked phone number.
    phone: Optional[str] = None

    zone_id: Optional[str] = None
    country: Optional[str] = None
    preferred_language: str = "en"

    accessibility_needs: list[str] = Field(default_factory=list)
    notification_consent: bool = False


class UserListItem(BaseModel):
    """Ops directory row — no passwords, phone masked."""
    user_id: str
    display_name: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    zone_id: Optional[str] = None
    country: Optional[str] = None
    preferred_language: str = "en"
    notification_consent: bool = False
    sms_eligible: bool = False


class UserProfileUpdate(BaseModel):
    display_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    role_title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    organization: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    work_email: Optional[str] = Field(
        default=None,
        min_length=5,
        max_length=254,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )

    # International E.164 format (Supports +20, +254, etc.)
    phone: Optional[str] = Field(
        default=None,
        pattern=r"^\+[1-9]\d{7,14}$",
    )

    zone_id: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    country: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    preferred_language: Optional[SupportedLanguage] = None
    accessibility_needs: Optional[list[AccessibilityNeed]] = None
    notification_consent: Optional[bool] = None

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, value):
        return _normalize_optional_phone(value)

    @field_validator("work_email", mode="before")
    @classmethod
    def normalize_work_email(cls, value):
        if isinstance(value, str):
            cleaned = value.strip().lower()
            return cleaned or None
        return value