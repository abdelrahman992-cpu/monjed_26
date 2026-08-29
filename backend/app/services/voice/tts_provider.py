"""
MONJED AI - TTS Provider Layer

Responsible for converting an approved
MONJED voice message into speech output.

This layer isolates MONJED from a specific
external Text-To-Speech provider.

Possible future providers:
- Google Cloud Text-to-Speech
- Azure Speech
- AWS Polly
- Africa's Talking Voice


CURRENT STATUS:
- MOCK provider for MVP/demo testing.


IMPORTANT:
- Does NOT generate alerts.
- Does NOT calculate risk.
- Does NOT make decisions.
- Does NOT modify message content.
"""


from datetime import (
    datetime,
    timezone,
)


# ============================================================
# SUPPORTED LANGUAGES
# ============================================================


SUPPORTED_LANGUAGES = {
    "en",
    "ar",
    "sw",
    "fr",
}


DEFAULT_LANGUAGE = "en"


# ============================================================
# HELPERS
# ============================================================


def _normalize_language(
    language,
) -> str:
    """
    Normalize TTS language.

    Unsupported values safely fall back to English.
    """

    if not isinstance(
        language,
        str,
    ):
        return DEFAULT_LANGUAGE


    normalized = (
        language
        .strip()
        .lower()
    )


    if normalized not in SUPPORTED_LANGUAGES:
        return DEFAULT_LANGUAGE


    return normalized


# ============================================================
# MOCK TTS PROVIDER
# ============================================================


def generate_voice_audio(
    text: str,
    language: str = "en",
) -> dict:
    """
    Convert approved alert text into voice output.

    CURRENT IMPLEMENTATION:
        MOCK TTS provider.

    This does not generate a real audio file yet.

    It returns the exact text that would be passed
    to a real TTS provider.

    Future implementation can replace this function
    without changing MONJED decision logic.
    """


    # --------------------------------------------------------
    # Validate text
    # --------------------------------------------------------

    if not isinstance(
        text,
        str,
    ):

        return {
            "success": False,
            "provider": "MOCK_TTS",
            "error": "Voice text must be a string.",
        }


    clean_text = text.strip()


    if not clean_text:

        return {
            "success": False,
            "provider": "MOCK_TTS",
            "error": "Voice text cannot be empty.",
        }


    # --------------------------------------------------------
    # Language
    # --------------------------------------------------------

    normalized_language = (
        _normalize_language(
            language
        )
    )


    # --------------------------------------------------------
    # Mock result
    # --------------------------------------------------------

    return {

        "success":
            True,

        "provider":
            "MOCK_TTS",

        "mock":
            True,

        "delivery_status":
            "simulated",

        "language":
            normalized_language,

        "text":
            clean_text,

        "audio_url":
            None,

        "generated_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

    }