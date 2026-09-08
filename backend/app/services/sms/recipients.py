"""
Resolve SMS recipients for alert delivery.

Priority:
1. Mongo users in the same zone with phone + notification consent
2. Sandbox fallback phones from env (development only)
"""

from app.services.sms.config import (
    AFRICAS_TALKING_SANDBOX_PHONES,
    AFRICAS_TALKING_USERNAME,
)

from database.connection import get_database 

def _sandbox_fallback_recipients() -> list[dict]:
    """
    Use configured sandbox phones when Africa's Talking sandbox
    is active and Mongo returned no eligible users.
    """

    if (AFRICAS_TALKING_USERNAME or "").strip().lower() != "sandbox":
        return []

    phones = [
        phone.strip()
        for phone in (AFRICAS_TALKING_SANDBOX_PHONES or "").split(",")
        if phone.strip()
    ]

    return [
        {
            "user_id": None,
            "phone": phone,
            "preferred_language": "en",
            "accessibility_needs": [],
        }
        for phone in phones
    ]


def get_sms_recipients_for_zone(
    zone_id: str,
) -> list[dict]:
    """
    Return structured SMS recipients for one operational zone.
    """

    normalized_zone = str(zone_id or "").strip()

    if not normalized_zone:
        return []

    recipients: list[dict] = []

    # recipients.py
# يفضل نقل الاستيراد للأعلى إذا لم يسبب Circular Import
try:
    from database.users_repository import get_alert_recipients_by_zone
except ImportError:
    get_alert_recipients_by_zone = None

def get_sms_recipients_for_zone(zone_id: str) -> list[dict]:
    normalized_zone = str(zone_id or "").strip()
    if not normalized_zone:
        return []

    recipients = []
    if get_alert_recipients_by_zone:
        try:
            recipients = get_alert_recipients_by_zone(normalized_zone)
        except Exception as exc:
            print(f"MONJED recipient selection warning: {type(exc).__name__}: {exc}")

    if recipients:
        return recipients

    fallback = _sandbox_fallback_recipients()
    if fallback:
        print(f"MONJED SMS: using sandbox fallback recipients for zone {normalized_zone}.")

    return fallback
