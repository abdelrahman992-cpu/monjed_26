from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from app.schemas.user import (
    UserListItem,
    UserProfileResponse,
    UserProfileUpdate,
)

from database.users_repository import (
    get_all_users,
    get_user,
    update_user,
)


router = APIRouter(
    prefix="/users",
    tags=["Users & Profiles"],
)


def _mask_phone(
    phone: str | None,
) -> str | None:
    """
    Return a masked international phone number.

    Full phone numbers remain stored in MongoDB for
    notification delivery but are not exposed to frontend.
    """

    if not phone:
        return None

    value = str(phone).strip()

    if not value.startswith("+"):
        # Still show something useful for ops without leaking full number.
        if len(value) <= 4:
            return "****"
        return value[:3] + ("*" * max(len(value) - 5, 2)) + value[-2:]

    digits = value[1:]

    if len(digits) <= 6:
        return "+****"

    visible_start = digits[:4]
    visible_end = digits[-2:]
    hidden_length = max(len(digits) - 6, 2)

    return "+" + visible_start + ("*" * hidden_length) + visible_end


def _clean_optional_text(value) -> str | None:
    if value is None:
        return None
    cleaned = str(value).strip()
    return cleaned or None


def _build_profile(user: dict) -> UserProfileResponse:
    notification_consent = bool(
        user.get(
            "notification_consent",
            user.get("notifications_enabled", False),
        )
    )

    stored_phone = user.get("phone") or user.get("phone_number")

    return UserProfileResponse(
        user_id=str(user.get("user_id", "")),
        display_name=user.get("display_name") or user.get("name"),
        role=user.get("role"),
        role_title=user.get("role_title"),
        organization=user.get("organization"),
        work_email=user.get("work_email") or user.get("email"),
        phone=_mask_phone(stored_phone),
        zone_id=user.get("zone_id"),
        country=user.get("country"),
        preferred_language=user.get("preferred_language", "en"),
        accessibility_needs=list(
            user.get("accessibility_needs", []) or []
        ),
        notification_consent=notification_consent,
    )


def _build_list_item(user: dict) -> UserListItem:
    stored_phone = user.get("phone") or user.get("phone_number")
    consent = bool(
        user.get(
            "notification_consent",
            user.get("notifications_enabled", False),
        )
    )
    has_phone = bool(stored_phone and str(stored_phone).strip())
    has_zone = bool(user.get("zone_id") and str(user.get("zone_id")).strip())

    return UserListItem(
        user_id=str(user.get("user_id", "")),
        display_name=user.get("display_name") or user.get("name"),
        role=user.get("role"),
        email=user.get("email") or user.get("work_email"),
        phone=_mask_phone(stored_phone),
        zone_id=user.get("zone_id"),
        country=user.get("country"),
        preferred_language=user.get("preferred_language", "en"),
        notification_consent=consent,
        sms_eligible=bool(consent and has_phone and has_zone),
    )


@router.get(
    "",
    response_model=list[UserListItem],
)
def list_platform_users(
    role: str | None = Query(default=None),
    zone_id: str | None = Query(default=None),
) -> list[UserListItem]:
    """
    List signed-up platform users for the operations console.

    Passwords and raw phone numbers are never returned.
    """

    try:
        users = get_all_users() or []
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"User directory unavailable: {type(exc).__name__}",
        ) from exc

    items = [_build_list_item(user) for user in users]

    if role is not None:
        wanted = role.strip().lower()
        items = [
            item
            for item in items
            if (item.role or "").lower() == wanted
        ]

    if zone_id is not None:
        wanted_zone = zone_id.strip()
        items = [
            item
            for item in items
            if (item.zone_id or "").strip() == wanted_zone
        ]

    return sorted(
        items,
        key=lambda item: (
            (item.display_name or "").lower(),
            item.user_id,
        ),
    )


@router.get(
    "/{user_id}/profile",
    response_model=UserProfileResponse,
)
def read_user_profile(user_id: str) -> UserProfileResponse:
    user = get_user(user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    return _build_profile(user)


@router.patch(
    "/{user_id}/profile",
    response_model=UserProfileResponse,
)
def update_user_profile(
    user_id: str,
    data: UserProfileUpdate,
) -> UserProfileResponse:
    existing_user = get_user(user_id)

    if existing_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    updates = data.model_dump(exclude_none=True)

    text_fields = {
        "display_name",
        "role_title",
        "organization",
        "work_email",
        "phone",
        "zone_id",
        "country",
    }

    for field_name in text_fields:
        if field_name in updates:
            cleaned = _clean_optional_text(updates[field_name])
            if cleaned is not None:
                updates[field_name] = cleaned

    if "work_email" in updates:
        updates["work_email"] = updates["work_email"].lower()

    if "accessibility_needs" in updates:
        updates["accessibility_needs"] = list(
            dict.fromkeys(updates["accessibility_needs"])
        )

    if "notification_consent" in updates:
        consent = bool(updates["notification_consent"])
        updates["notification_consent"] = consent
        updates["notifications_enabled"] = consent

    if updates:
        update_user(user_id, updates)

    updated_user = get_user(user_id)

    if updated_user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    return _build_profile(updated_user)
