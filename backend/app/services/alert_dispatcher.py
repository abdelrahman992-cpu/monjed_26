"""
MONJED AI - Alert Dispatcher

Responsible only for delivering validated alerts
through available communication channels.

Architecture:

Normalized Alert
        |
        |
        +---- Dashboard
        |
        +---- SMS
        |
        +---- Voice


IMPORTANT:
- Does NOT generate alerts.
- Does NOT calculate risk.
- Does NOT modify decisions.
- Does NOT make safety decisions.
- Only coordinates delivery.
"""
from copy import deepcopy

from AI.ai_alert.alert_formatter import (
    format_dashboard_alert,
)


from app.services.sms.sms_service import (
    send_alert_sms,
)


from app.services.voice.voice_service import (
    send_voice_alert,
)



# ============================================================
# VALIDATION
# ============================================================


def _validate_alert(
    alert: dict,
):

    if not isinstance(
        alert,
        dict,
    ):

        raise TypeError(
            "alert must be a dictionary."
        )


    if not alert:

        raise ValueError(
            "alert cannot be empty."
        )



# ============================================================
# NOTIFICATION CHECK
# ============================================================


def _notification_allowed(
    alert: dict,
) -> bool:
    """
    Check whether active notification
    channels are allowed.

    Decision Engine is the source
    of this information.
    """


    return bool(

        alert.get(

            "notification_required",

            False,

        )

    )



# ============================================================
# DASHBOARD DELIVERY
# ============================================================


def prepare_dashboard_alert(
    alert: dict,
) -> dict:
    """
    Dashboard always receives updates.

    Monitoring states are displayed
    even when notification is disabled.
    """


    return format_dashboard_alert(
        alert
    )



# ============================================================
# SMS DELIVERY
# ============================================================


SUPPORTED_RECIPIENT_LANGUAGES = {
    "en",
    "ar",
    "sw",
    "fr",
}


def _normalize_sms_recipient(
    recipient,
) -> dict:
    """
    Normalize one SMS recipient.

    Supports the new recipient structure:

    {
        "user_id": "...",
        "phone": "...",
        "preferred_language": "ar",
        "accessibility_needs": [...]
    }

    A plain phone string is still supported
    for backward compatibility with existing tests.
    """


    # --------------------------------------------------------
    # Backward compatibility
    # --------------------------------------------------------

    if isinstance(
        recipient,
        str,
    ):

        phone = recipient.strip()

        if not phone:
            raise ValueError(
                "Recipient phone cannot be empty."
            )

        return {
            "user_id":
                None,

            "phone":
                phone,

            "preferred_language":
                "en",

            "accessibility_needs":
                [],
        }


    # --------------------------------------------------------
    # Structured recipient
    # --------------------------------------------------------

    if not isinstance(
        recipient,
        dict,
    ):

        raise TypeError(
            "SMS recipient must be a dictionary or phone string."
        )


    phone = (
        recipient.get(
            "phone"
        )
        or recipient.get(
            "phone_number"
        )
    )


    if not isinstance(
        phone,
        str,
    ) or not phone.strip():

        raise ValueError(
            "Recipient phone is missing."
        )


    phone = phone.strip()


    language = str(
        recipient.get(
            "preferred_language",
            "en",
        )
    ).strip().lower()


    if language not in SUPPORTED_RECIPIENT_LANGUAGES:

        language = "en"


    accessibility_needs = recipient.get(
        "accessibility_needs",
        [],
    )


    if not isinstance(
        accessibility_needs,
        list,
    ):

        accessibility_needs = []


    return {
        "user_id":
            recipient.get(
                "user_id"
            ),

        "phone":
            phone,

        "preferred_language":
            language,

        "accessibility_needs":
            accessibility_needs,
    }



def send_sms_alert(
    alert: dict,
    recipients: list,
) -> list[dict]:
    """
    Send an emergency SMS to each recipient
    using that recipient's preferred language.

    IMPORTANT:
    - Scientific risk is unchanged.
    - Decision is unchanged.
    - notification_required is unchanged.
    - Only communication metadata is adapted.
    """


    if not isinstance(
        recipients,
        list,
    ):

        raise TypeError(
            "recipients must be a list."
        )


    results = []


    for raw_recipient in recipients:


        normalized_recipient = None


        try:

            normalized_recipient = (
                _normalize_sms_recipient(
                    raw_recipient
                )
            )


            # Each recipient receives an isolated
            # communication copy of the SAME alert.
            localized_alert = deepcopy(
                alert
            )


            localized_alert[
                "language"
            ] = normalized_recipient[
                "preferred_language"
            ]


            localized_alert[
                "accessibility_needs"
            ] = deepcopy(
                normalized_recipient[
                    "accessibility_needs"
                ]
            )


            result = send_alert_sms(

                normalized_recipient[
                    "phone"
                ],

                localized_alert,

            )


        except Exception as error:


            result = {

                "success":
                    False,

                "error":
                    str(error),

            }


        delivery_record = {

            "user_id":
                (
                    normalized_recipient.get(
                        "user_id"
                    )
                    if normalized_recipient
                    else None
                ),

            "preferred_language":
                (
                    normalized_recipient.get(
                        "preferred_language",
                        "en",
                    )
                    if normalized_recipient
                    else "en"
                ),

            "result":
                result,

        }


        # Preserve current delivery structure
        # for existing persistence/debugging logic.
        if normalized_recipient:

            delivery_record[
                "phone"
            ] = normalized_recipient[
                "phone"
            ]


        results.append(
            delivery_record
        )


    return results

# ============================================================
# VOICE DELIVERY
# ============================================================


def prepare_voice_alert(
    alert: dict,
) -> dict:
    """
    Generate voice alert.

    Voice provider is isolated
    inside voice service layer.
    """


    return send_voice_alert(
        alert
    )



# ============================================================
# FULL DISPATCH
# ============================================================


def dispatch_alert(
    alert: dict,
    sms_recipients: list | None = None,
) -> dict:

    """
    Main MONJED delivery coordinator.


    Behavior:

    notification_required = False

        Dashboard only


    notification_required = True

        Dashboard
        SMS
        Voice

    """


    _validate_alert(
        alert
    )



    result = {


        "dashboard":

            prepare_dashboard_alert(
                alert
            ),



        "sms":

            [],



        "voice":

            None,



        "notification_required":

            _notification_allowed(
                alert
            ),

    }



    # ========================================================
    # Emergency Channels
    # ========================================================


    if not _notification_allowed(
        alert
    ):


        result["voice"] = {

            "success":
                False,

            "message":
                "Notification not required. Dashboard update only.",

        }


        return result



    # ========================================================
    # SMS
    # ========================================================


    if sms_recipients:


        result["sms"] = send_sms_alert(

            alert,

            sms_recipients,

        )



    # ========================================================
    # Voice
    # ========================================================


    try:


        result["voice"] = prepare_voice_alert(

            alert

        )


    except Exception as error:


        result["voice"] = {

            "success":
                False,

            "error":
                str(error),

        }



    return result