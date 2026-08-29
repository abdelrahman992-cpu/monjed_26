"""
MONJED SMS Service Layer

Single interface between MONJED backend
and SMS delivery providers.

Architecture:

Normalized MONJED Alert
          |
          ↓
SMS Service Layer
          |
          ↓
SMS Formatter
          |
          ↓
SMS Provider
          |
          ↓
Delivery Result


Responsibilities:
- Validate SMS request.
- Convert alert into SMS message.
- Communicate with provider.
- Normalize provider response.


IMPORTANT:
- Does NOT calculate risk.
- Does NOT make decisions.
- Does NOT modify alert content.
- Provider can be replaced safely.
"""


from app.services.sms.africas_talking import (
    send_sms as send_provider_sms,
)


from app.services.sms.sms_formatter import (
    format_sms_alert,
)



# ============================================================
# CONSTANTS
# ============================================================


MAX_SMS_LENGTH = 1600



# ============================================================
# HELPERS
# ============================================================


def _validate_phone_number(
    phone_number: str,
) -> bool:
    """
    Basic phone validation.
    """


    if not isinstance(
        phone_number,
        str,
    ):

        return False



    cleaned = phone_number.strip()



    return len(cleaned) >= 8





def _normalize_phone(
    phone_number: str,
) -> str:
    """
    Normalize phone input.
    """


    return phone_number.strip()



# ============================================================
# SEND ALERT SMS
# ============================================================


def send_alert_sms(
    phone_number: str,
    alert: dict,
) -> dict:
    """
    Send MONJED emergency alert SMS.


    Input:

        phone_number:
            Destination phone.


        alert:
            Normalized MONJED alert.


    Output:

        {
            "success": True/False,
            "provider": "...",
            "response": {}
        }

    """



    # --------------------------------------------------------
    # Validate phone
    # --------------------------------------------------------


    if not _validate_phone_number(
        phone_number
    ):

        return {

            "success": False,

            "stage":
                "validation",

            "error":
                "Invalid phone number",

        }



    phone_number = _normalize_phone(
        phone_number
    )



    # --------------------------------------------------------
    # Validate alert
    # --------------------------------------------------------


    if not isinstance(
        alert,
        dict,
    ):

        return {

            "success": False,

            "stage":
                "validation",

            "error":
                "Alert payload must be a dictionary",

        }



    if not alert:

        return {

            "success": False,

            "stage":
                "validation",

            "error":
                "Alert payload cannot be empty",

        }



    # --------------------------------------------------------
    # Format SMS message
    # --------------------------------------------------------


    try:

        message = format_sms_alert(
            alert
        )


    except Exception as error:


        return {

            "success": False,

            "stage":
                "formatter",

            "error":
                str(error),

        }



    if not message:

        return {

            "success": False,

            "stage":
                "formatter",

            "error":
                "Generated SMS message is empty",

        }



    # --------------------------------------------------------
    # Validate message length
    # --------------------------------------------------------


    if len(message) > MAX_SMS_LENGTH:

        message = message[
            :MAX_SMS_LENGTH
        ]



    # --------------------------------------------------------
    # Send through provider
    # --------------------------------------------------------


    try:

        provider_result = send_provider_sms(

            phone_number,

            message,

        )


    except Exception as error:


        return {

            "success": False,

            "stage":
                "provider",

            "error":
                str(error),

        }



    # --------------------------------------------------------
    # Unified response
    # --------------------------------------------------------


    return {

        "success":

            provider_result.get(
                "success",
                False,
            )
            if isinstance(
                provider_result,
                dict,
            )
            else False,


        "provider":

            "AFRICAS_TALKING",


        "phone":

            phone_number,


        "message":

            message,


        "response":

            provider_result,

    }