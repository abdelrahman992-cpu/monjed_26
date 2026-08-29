from datetime import datetime

from pydantic import BaseModel, Field, field_validator


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


class ContactRequest(BaseModel):

    name: str = Field(
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

    phone: str | None = Field(
        default=None,
        pattern=r"^\+[1-9]\d{7,14}$",
    )

    subject: str | None = Field(
        default=None,
        max_length=150,
    )

    message: str = Field(
        ...,
        min_length=5,
        max_length=2000,
    )

    @field_validator("phone", mode="before")
    @classmethod
    def normalize_phone(cls, value):
        return _normalize_optional_phone(value)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("subject", mode="before")
    @classmethod
    def normalize_subject(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            cleaned = value.strip()
            return cleaned or None
        return value


class ContactResponse(BaseModel):

    contact_id: str

    status: str = "received"

    created_at: datetime
