"""
MONJED AI - Voice Service Layer

Responsible for preparing MONJED alerts
for voice delivery.

Architecture:

Normalized Alert
        |
        ↓
Voice Service
        |
        ↓
TTS Provider


IMPORTANT:
- Does NOT calculate risk.
- Does NOT generate alerts.
- Does NOT make decisions.
- Does NOT modify approved actions.
- Does NOT change notification logic.
"""


from backend.app.services.voice.tts_provider import (
    generate_voice_audio,
)


# ============================================================
# HELPERS
# ============================================================


def _safe_dict(value) -> dict:
    """
    Safely return a dictionary.
    """

    return value if isinstance(value, dict) else {}



def _safe_list(value) -> list:
    """
    Safely return a list.
    """

    return value if isinstance(value, list) else []



def _clean_text(value, default="") -> str:
    """
    Normalize unnecessary whitespace without
    changing the meaning of the text.
    """

    if value is None:
        return default

    text = " ".join(
        str(value).split()
    )

    return text if text else default



def _build_location(
    country: str,
    zone_id: str,
) -> str:
    """
    Build a voice-friendly location.
    """

    parts = []

    if country:
        parts.append(country)

    if zone_id:
        parts.append(zone_id)

    return ", ".join(parts)


# ============================================================
# VOICE MESSAGE BUILDER
# ============================================================


def build_voice_message(
    alert: dict,
) -> str:
    """
    Convert a normalized MONJED alert into
    a clear voice-friendly message.

    Example:

    MONJED alert.
    High flood risk detected in Kenya, Zone Test 01.
    Action: Move to a safer elevated area immediately.
    Safety: Avoid flooded roads and do not cross moving water.
    """

    if not isinstance(alert, dict):
        raise TypeError(
            "alert must be a dictionary."
        )


    message_parts = []


    # --------------------------------------------------------
    # Opening
    # --------------------------------------------------------

    message_parts.append(
        "MONJED alert."
    )


    # --------------------------------------------------------
    # Hazard information
    # --------------------------------------------------------

    hazards = _safe_list(
        alert.get(
            "hazards",
            [],
        )
    )

    hazard = _safe_dict(
        hazards[0]
        if hazards
        else {}
    )


    hazard_type = _clean_text(
        hazard.get("type")
    ).lower()


    risk_level = _clean_text(
        hazard.get("risk_level")
    ).lower()


    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------

    country = _clean_text(
        alert.get("country")
    )

    zone_id = _clean_text(
        alert.get("zone_id")
    )

    location = _build_location(
        country=country,
        zone_id=zone_id,
    )


    # --------------------------------------------------------
    # Main hazard sentence
    # --------------------------------------------------------

    if hazard_type and risk_level:

        hazard_sentence = (
            f"{risk_level.capitalize()} "
            f"{hazard_type} risk detected"
        )

        if location:
            hazard_sentence += (
                f" in {location}"
            )

        hazard_sentence += "."

        message_parts.append(
            hazard_sentence
        )


    elif hazard_type:

        hazard_sentence = (
            f"{hazard_type.capitalize()} "
            f"risk detected"
        )

        if location:
            hazard_sentence += (
                f" in {location}"
            )

        hazard_sentence += "."

        message_parts.append(
            hazard_sentence
        )


    elif location:

        message_parts.append(
            f"Alert for {location}."
        )


    # --------------------------------------------------------
    # Backend-approved decision
    # --------------------------------------------------------

    decision = _safe_dict(
        alert.get(
            "final_decision",
            {},
        )
    )


    current_action = _clean_text(
        decision.get(
            "current_action"
        )
    )


    if current_action:

        message_parts.append(
            f"Action: {current_action}"
        )


    backup_action = _clean_text(
        decision.get(
            "backup_action"
        )
    )


    if backup_action:

        message_parts.append(
            f"Safety: {backup_action}"
        )


    # --------------------------------------------------------
    # Personalized accessibility instructions
    # --------------------------------------------------------
    #
    # These should only contain instructions already approved
    # upstream for the specific recipient.
    #
    # Voice Service does not generate accessibility advice.
    # --------------------------------------------------------

    accessibility = _safe_list(
        decision.get(
            "accessibility_instructions",
            [],
        )
    )


    for instruction in accessibility:

        clean_instruction = _clean_text(
            instruction
        )

        if clean_instruction:
            message_parts.append(
                clean_instruction
            )


    return " ".join(
        message_parts
    )


# ============================================================
# SEND VOICE ALERT
# ============================================================


def send_voice_alert(
    alert: dict,
) -> dict:
    """
    Prepare and send a MONJED alert
    through the configured TTS provider.

    The current provider is a mock provider.
    """

    if not isinstance(alert, dict):
        raise TypeError(
            "alert must be a dictionary."
        )


    message = build_voice_message(
        alert
    )


    language = _clean_text(
        alert.get(
            "language"
        ),
        "en",
    ).lower()


    return generate_voice_audio(
        text=message,
        language=language,
    )