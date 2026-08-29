from typing import Literal

from pydantic import BaseModel, Field, field_validator


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


def _normalize_optional_phone(value):
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


class UserProfileResponse(BaseModel):
    user_id: str
    display_name: str | None = None
    role: str | None = None
    role_title: str | None = None
    organization: str | None = None
    work_email: str | None = None

    # Frontend receives only a masked phone number.
    phone: str | None = None

    zone_id: str | None = None
    country: str | None = None
    preferred_language: str = "en"

    accessibility_needs: list[str] = Field(
        default_factory=list
    )

    notification_consent: bool = False


class UserListItem(BaseModel):
    """Ops directory row — no passwords, phone masked."""

    user_id: str
    display_name: str | None = None
    role: str | None = None
    email: str | None = None
    phone: str | None = None
    zone_id: str | None = None
    country: str | None = None
    preferred_language: str = "en"
    notification_consent: bool = False
    sms_eligible: bool = False


class UserProfileUpdate(BaseModel):
    display_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    role_title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    organization: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    work_email: str | None = Field(
        default=None,
        min_length=5,
        max_length=254,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )

    # International E.164 format.
    # Supports Egypt +20, Kenya +254, and other countries.
    phone: str | None = Field(
        default=None,
        pattern=r"^\+[1-9]\d{7,14}$",
    )

    zone_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    country: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    preferred_language: SupportedLanguage | None = None

    accessibility_needs: list[AccessibilityNeed] | None = None

    notification_consent: bool | None = None

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
