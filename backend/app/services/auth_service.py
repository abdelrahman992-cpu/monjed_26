import base64
import hashlib
import hmac
import secrets


PBKDF2_ITERATIONS = 200_000


def hash_password(
    password: str,
) -> str:

    salt = secrets.token_bytes(
        16
    )

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(
            "utf-8"
        ),
        salt,
        PBKDF2_ITERATIONS,
    )

    return (
        "pbkdf2_sha256"
        f"${PBKDF2_ITERATIONS}"
        f"${base64.b64encode(salt).decode()}"
        f"${base64.b64encode(password_hash).decode()}"
    )


def verify_password(
    password: str,
    stored_hash: str,
) -> bool:

    try:
        (
            algorithm,
            iterations,
            salt_b64,
            hash_b64,
        ) = stored_hash.split(
            "$",
            3,
        )

        if algorithm != "pbkdf2_sha256":
            return False

        salt = base64.b64decode(
            salt_b64
        )

        expected_hash = base64.b64decode(
            hash_b64
        )

        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(
                "utf-8"
            ),
            salt,
            int(
                iterations
            ),
        )

        return hmac.compare_digest(
            actual_hash,
            expected_hash,
        )

    except (
        ValueError,
        TypeError,
    ):
        return False


def generate_access_token() -> str:
    """
    Generate an opaque access token.

    The current demo frontend can use this token
    as authenticated-session state.

    Passwords are never included in the token.
    """

    return secrets.token_urlsafe(
        32
    )
