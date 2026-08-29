from typing import Literal

from pydantic import BaseModel, Field, field_validator


RegisterRole = Literal[
    "citizen",
    "volunteer",
]


def _normalize_optional_phone(value):
    """Treat blank / spaced phone as missing; keep E.164 digits with +."""
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


def _normalize_optional_text(value):
    if value is None:
        return None
    if not isinstance(value, str):
        return value
    cleaned = value.strip()
    return cleaned or None


class RegisterRequest(BaseModel):

    display_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    email: str = Field(
        ...,
        min_length=5,
        max_length=254,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )

    phone: str | None = Field(
        default=None,
        pattern=r"^\+[1-9]\d{7,14}$",
    )

    role: RegisterRole = "citizen"

    zone_id: str | None = Field(
        default=None,
        max_length=100,
    )

    country: str | None = Field(
        default=None,
        max_length=100,
    )

    preferred_language: Literal[
        "en",
        "ar",
        "sw",
        "fr",
    ] = "en"

    accessibility_needs: list[str] = Field(
        default_factory=list
    )

    notification_consent: bool = True

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, value):
        return _normalize_optional_phone(value)

    @field_validator("zone_id", "country", mode="before")
    @classmethod
    def normalize_optional_strings(cls, value):
        return _normalize_optional_text(value)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("display_name", mode="before")
    @classmethod
    def normalize_display_name(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value


class LoginRequest(BaseModel):

    # Email or international phone number.
    identifier: str = Field(
        ...,
        min_length=3,
        max_length=254,
    )

    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
    )

    @field_validator("identifier", mode="before")
    @classmethod
    def normalize_identifier(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value


class AuthUserResponse(BaseModel):

    user_id: str

    display_name: str | None = None

    role: str

    email: str | None = None

    phone: str | None = None

    zone_id: str | None = None

    country: str | None = None

    preferred_language: str = "en"


class AuthResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"

    user: AuthUserResponse
