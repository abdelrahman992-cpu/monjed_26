from uuid import uuid4

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)

from app.schemas.auth import (
    AuthResponse,
    AuthUserResponse,
    LoginRequest,
    RegisterRequest,
)

from app.services.auth_service import (
    generate_access_token,
    hash_password,
    verify_password,
)

from database.users_repository import (
    create_user,
    get_user_by_email,
    get_user_by_phone,
)

from app.schemas.contact import (
    ContactRequest,
    ContactResponse,
)

from database.contact_repository import (
    save_contact_message,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def _safe_phone(
    phone,
):
    if not phone:
        return None

    value = str(
        phone
    ).strip()

    if len(value) < 7:
        return None

    return (
        value[:5]
        + ("*" * max(
            len(value) - 7,
            2,
        ))
        + value[-2:]
    )


def _build_auth_user(
    user: dict,
) -> AuthUserResponse:

    return AuthUserResponse(
        user_id=str(
            user.get(
                "user_id",
                "",
            )
        ),

        display_name=(
            user.get(
                "display_name"
            )
            or user.get(
                "name"
            )
        ),

        role=user.get(
            "role",
            "citizen",
        ),

        email=(
            user.get(
                "email"
            )
            or user.get(
                "work_email"
            )
        ),

        phone=_safe_phone(
            user.get(
                "phone"
            )
            or user.get(
                "phone_number"
            )
        ),

        zone_id=user.get(
            "zone_id"
        ),

        country=user.get(
            "country"
        ),

        preferred_language=user.get(
            "preferred_language",
            "en",
        ),
    )


def _authenticate(
    data: LoginRequest,
    required_role: str | None = None,
) -> AuthResponse:

    identifier = (
        data.identifier
        .strip()
    )

    if "@" in identifier:

        user = get_user_by_email(
            identifier
        )

    else:

        user = get_user_by_phone(
            identifier
        )

    # Do not reveal whether the account exists.
    if user is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    password_hash = user.get(
        "password_hash"
    )

    if (
        not password_hash
        or not verify_password(
            data.password,
            password_hash,
        )
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    if (
        required_role is not None
        and user.get(
            "role"
        ) != required_role
    ):

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account does not have the required role.",
        )

    return AuthResponse(
        access_token=generate_access_token(),
        user=_build_auth_user(
            user
        ),
    )


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
) -> AuthResponse:

    email = (
        data.email
        .strip()
        .lower()
    )

    if get_user_by_email(
        email
    ) is not None:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    phone = (
        data.phone.strip()
        if data.phone
        else None
    )

    if (
        phone
        and get_user_by_phone(
            phone
        ) is not None
    ):

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this phone number already exists.",
        )

    user_id = (
        "user_"
        + uuid4().hex
    )

    user = {
        "user_id":
            user_id,

        "display_name":
            data.display_name.strip(),

        "email":
            email,

        "password_hash":
            hash_password(
                data.password
            ),

        "role":
            data.role,

        "zone_id":
            (
                data.zone_id.strip()
                if data.zone_id
                else None
            ),

        "country":
            (
                data.country.strip()
                if data.country
                else None
            ),

        "preferred_language":
            data.preferred_language,

        "accessibility_needs":
            list(
                dict.fromkeys(
                    data.accessibility_needs
                )
            ),

        "notification_consent":
            data.notification_consent,

        "notifications_enabled":
            data.notification_consent,
    }

    if phone:
        user[
            "phone"
        ] = phone

    create_user(
        user
    )

    return AuthResponse(
        access_token=generate_access_token(),
        user=_build_auth_user(
            user
        ),
    )


@router.post(
    "/login",
    response_model=AuthResponse,
)
def login(
    data: LoginRequest,
) -> AuthResponse:

    return _authenticate(
        data
    )


@router.post(
    "/admin",
    response_model=AuthResponse,
)
def admin_login(
    data: LoginRequest,
) -> AuthResponse:
    """
    Admin-specific login used by the operations frontend.

    Only accounts whose stored role is exactly 'admin'
    are accepted.
    """

    return _authenticate(
        data,
        required_role="admin",
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
    """
    Receive a public contact/support message.

    Contact submissions do not affect:
    - scientific risk
    - decisions
    - community evidence
    - responder matching
    """

    payload = {
        "name":
            data.name.strip(),

        "email":
            data.email.strip().lower(),

        "phone":
            (
                data.phone.strip()
                if data.phone
                else None
            ),

        "subject":
            (
                data.subject.strip()
                if data.subject
                else None
            ),

        "message":
            data.message.strip(),
    }

    record = save_contact_message(
        payload
    )

    return ContactResponse(
        contact_id=record[
            "contact_id"
        ],

        status=record[
            "status"
        ],

        created_at=record[
            "created_at"
        ],
    )