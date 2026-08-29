"""
MONJED SMS Multilingual Test

Tests SMS formatting for:
- English
- Arabic
- Swahili
- French

No SMS is sent.
No provider is called.
"""


from backend.app.services.sms.sms_formatter import (
    format_sms_alert,
)


# ============================================================
# TEST DATA
# ============================================================


LANGUAGES = {
    "en": "ENGLISH",
    "ar": "ARABIC",
    "sw": "SWAHILI",
    "fr": "FRENCH",
}


BASE_ALERT = {

    "country": "Kenya",

    "zone_id": "Zone Test 01",

    "hazards": [
        {
            "type": "flood",
            "risk_level": "high",
            "risk_score": 75.0,
        }
    ],

    "final_decision": {

        "decision_status":
            "action_adjusted",

        "notification_required":
            True,

        "current_action":
            "Move to a safer elevated area immediately.",

        "backup_action":
            "Avoid flooded roads and do not cross moving water.",

    },

}


# ============================================================
# RUN TEST
# ============================================================


for language_code, language_name in LANGUAGES.items():

    alert = {
        **BASE_ALERT,
        "language": language_code,
    }

    message = format_sms_alert(
        alert
    )

    print(
        "\n"
        "========================================"
    )

    print(
        f"{language_name} ({language_code})"
    )

    print(
        "========================================\n"
    )

    print(
        message
    )

    print(
        f"\nCharacters: {len(message)}"
    )