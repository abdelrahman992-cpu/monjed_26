"""
MONJED SMS Formatter

Converts normalized MONJED alerts into
clear, compact, human-readable emergency SMS.

Design goals:
- Fast to understand.
- Clear even if line breaks are collapsed.
- Minimal unnecessary text.
- Preserve backend-approved actions exactly.
- Support English, Arabic, Swahili, and French.

IMPORTANT:
- Does NOT calculate risk.
- Does NOT make decisions.
- Does NOT modify risk values.
- Does NOT invent or rewrite actions.
"""


# ============================================================
# SUPPORTED LANGUAGES
# ============================================================
from app.services.sms.action_localizer import (
    localize_action,
)

SUPPORTED_LANGUAGES = {
    "en",
    "ar",
    "sw",
    "fr",
}


# ============================================================
# TRANSLATIONS
# ============================================================


TRANSLATIONS = {

    "title": {
        "en": "MONJED ALERT",
        "ar": "تنبيه MONJED",
        "sw": "TAHADHARI YA MONJED",
        "fr": "ALERTE MONJED",
    },

    "action": {
        "en": "ACTION",
        "ar": "الإجراء",
        "sw": "HATUA",
        "fr": "ACTION",
    },

    "safety": {
        "en": "SAFETY",
        "ar": "السلامة",
        "sw": "USALAMA",
        "fr": "SÉCURITÉ",
    },

    "unknown_hazard": {
        "en": "HAZARD",
        "ar": "خطر",
        "sw": "HATARI",
        "fr": "DANGER",
    },

    "default_action": {
        "en": "Follow official safety guidance.",
        "ar": "اتبع تعليمات السلامة الرسمية.",
        "sw": "Fuata maelekezo rasmi ya usalama.",
        "fr": "Suivez les consignes officielles de sécurité.",
    },

}


# ============================================================
# HAZARD NAMES
# ============================================================


HAZARD_NAMES = {

    "flood": {
        "en": "FLOOD",
        "ar": "فيضان",
        "sw": "MAFURIKO",
        "fr": "INONDATION",
    },

    "earthquake": {
        "en": "EARTHQUAKE",
        "ar": "زلزال",
        "sw": "TETEMEKO",
        "fr": "SÉISME",
    },

}


# ============================================================
# RISK LEVEL NAMES
# ============================================================


RISK_LEVEL_NAMES = {

    "low": {
        "en": "LOW",
        "ar": "منخفض",
        "sw": "NDOGO",
        "fr": "FAIBLE",
    },

    "moderate": {
        "en": "MODERATE",
        "ar": "متوسط",
        "sw": "WASTANI",
        "fr": "MODÉRÉ",
    },

    "high": {
        "en": "HIGH",
        "ar": "مرتفع",
        "sw": "KUBWA",
        "fr": "ÉLEVÉ",
    },

    "critical": {
        "en": "CRITICAL",
        "ar": "حرج",
        "sw": "KUBWA SANA",
        "fr": "CRITIQUE",
    },

    "unknown": {
        "en": "UNKNOWN",
        "ar": "غير معروف",
        "sw": "HAIJULIKANI",
        "fr": "INCONNU",
    },

}


# ============================================================
# HELPERS
# ============================================================


def _translate(
    key: str,
    language: str,
) -> str:
    """
    Safe translation lookup.
    """

    language_map = TRANSLATIONS.get(
        key,
        {},
    )

    return language_map.get(
        language,
        language_map.get(
            "en",
            key,
        ),
    )



def _normalize_language(
    language,
) -> str:
    """
    Normalize requested communication language.

    Supported base languages:
    - en
    - ar
    - sw
    - fr

    Regional variants such as ar-EG, fr-FR,
    sw-KE, and en_US are reduced to the
    supported base language.

    Unsupported values safely fall back to English.
    """

    if not isinstance(
        language,
        str,
    ):
        return "en"

    normalized = (
        language
        .strip()
        .lower()
        .replace(
            "_",
            "-",
        )
    )

    if not normalized:
        return "en"

    base_language = normalized.split(
        "-",
        1,
    )[0]

    if base_language not in SUPPORTED_LANGUAGES:
        return "en"

    return base_language


def _safe_dict(
    value,
) -> dict:
    """
    Safely return a dictionary.
    """

    return value if isinstance(
        value,
        dict,
    ) else {}



def _safe_list(
    value,
) -> list:
    """
    Safely return a list.
    """

    return value if isinstance(
        value,
        list,
    ) else []



def _clean_text(
    value,
    default="",
) -> str:
    """
    Normalize unnecessary whitespace
    without changing message meaning.
    """

    if value is None:
        return default

    text = " ".join(
        str(value).split()
    )

    return text if text else default



def _localized_hazard(
    hazard_type: str,
    language: str,
) -> str:
    """
    Return localized hazard name.
    """

    hazard_key = _clean_text(
        hazard_type,
        "unknown",
    ).lower()

    language_map = HAZARD_NAMES.get(
        hazard_key,
    )

    if not language_map:
        return _translate(
            "unknown_hazard",
            language,
        )

    return language_map.get(
        language,
        language_map["en"],
    )



def _localized_risk(
    risk_level: str,
    language: str,
) -> str:
    """
    Return localized risk level.
    """

    risk_key = _clean_text(
        risk_level,
        "unknown",
    ).lower()

    language_map = RISK_LEVEL_NAMES.get(
        risk_key,
        RISK_LEVEL_NAMES["unknown"],
    )

    return language_map.get(
        language,
        language_map["en"],
    )



def _build_risk_heading(
    hazard_type: str,
    risk_level: str,
    language: str,
) -> str:
    """
    Build the main emergency headline.

    Example:
        HIGH FLOOD RISK
    """

    hazard = _localized_hazard(
        hazard_type,
        language,
    )

    risk = _localized_risk(
        risk_level,
        language,
    )

    if language == "ar":
        return f"خطر {hazard} - المستوى {risk}"

    if language == "sw":
        return f"{hazard} - HATARI {risk}"

    if language == "fr":
        return f"{hazard} - RISQUE {risk}"

    return f"{risk} {hazard} RISK"



def _build_location(
    country: str,
    zone_id: str,
) -> str:
    """
    Build compact location text.
    """

    parts = []

    if country:
        parts.append(
            country
        )

    if zone_id:
        parts.append(
            zone_id
        )

    return " - ".join(
        parts
    )



def _ensure_sentence(
    text: str,
) -> str:
    """
    Ensure section ends clearly.

    This improves readability if a provider
    collapses line breaks.
    """

    text = _clean_text(
        text
    )

    if not text:
        return ""

    if text.endswith(
        (
            ".",
            "!",
            "?",
            "؟",
        )
    ):
        return text

    return f"{text}."


# ============================================================
# MAIN FORMATTER
# ============================================================


def format_sms_alert(
    alert: dict,
) -> str:
    """
    Convert normalized MONJED alert into
    a concise emergency SMS.

    Example:

    MONJED ALERT - HIGH FLOOD RISK.
    Kenya - Zone Test 01.
    ACTION: Move to a safer elevated area.
    SAFETY: Avoid flooded roads and moving water.
    """

    if not isinstance(
        alert,
        dict,
    ):
        return ""



    # --------------------------------------------------------
    # Language
    # --------------------------------------------------------


    language = _normalize_language(
        alert.get(
            "language",
            "en",
        )
    )



    # --------------------------------------------------------
    # Hazard
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
        hazard.get(
            "type",
        ),
        "unknown",
    )


    risk_level = _clean_text(
        hazard.get(
            "risk_level",
        ),
        "unknown",
    )



    # --------------------------------------------------------
    # Location
    # --------------------------------------------------------


    country = _clean_text(
        alert.get(
            "country",
        )
    )


    zone_id = _clean_text(
        alert.get(
            "zone_id",
        )
    )


    location = _build_location(
        country=country,
        zone_id=zone_id,
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
        "current_action",
    )
)


    if current_action:

        current_action = localize_action(
            current_action,
            language,
        )

    else:

        # Defensive fallback only.
        # Normal MONJED decisions should always
        # provide current_action.
        current_action = _translate(
            "default_action",
            language,
        )


    backup_action = _clean_text(
        decision.get(
            "backup_action",
        )
    )


    if backup_action:

        backup_action = localize_action(
            backup_action,
            language,
        )

    # --------------------------------------------------------
    # Headline
    # --------------------------------------------------------


    risk_heading = _build_risk_heading(
        hazard_type=hazard_type,
        risk_level=risk_level,
        language=language,
    )



    # --------------------------------------------------------
    # Build message
    # --------------------------------------------------------


    lines = []


    lines.append(
        _ensure_sentence(
            f"{_translate('title', language)} - {risk_heading}"
        )
    )


    if location:

        lines.append(
            _ensure_sentence(
                location
            )
        )


    lines.append(
        f"{_translate('action', language)}: "
        f"{_ensure_sentence(current_action)}"
    )


    if backup_action:

        lines.append(
            f"{_translate('safety', language)}: "
            f"{_ensure_sentence(backup_action)}"
        )



    return "\n".join(
        lines
    )