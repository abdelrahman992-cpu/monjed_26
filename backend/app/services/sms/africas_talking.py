"""
MONJED AI - Africa's Talking SMS Provider

Low-level SMS communication layer.

Responsibilities:
- Communicate with Africa's Talking REST API.
- Send SMS requests.
- Return normalized provider responses.

IMPORTANT:
- Contains NO MONJED business logic.
- Does NOT calculate risk.
- Does NOT format alerts.
- Can be replaced with another provider.
"""


import json
import urllib.parse
import urllib.request
import urllib.error



from app.services.sms.config import (
    AFRICAS_TALKING_USERNAME,
    AFRICAS_TALKING_API_KEY,
    AFRICAS_TALKING_SENDER_ID,
)



# ============================================================
# CONFIGURATION
# ============================================================


AFRICAS_TALKING_SMS_URL = (
    "https://api.sandbox.africastalking.com/version1/messaging"
)


REQUEST_TIMEOUT_SECONDS = 15



# ============================================================
# HELPERS
# ============================================================


def _validate_input(
    phone_number: str,
    message: str,
) -> str | None:


    if not AFRICAS_TALKING_USERNAME:
        return "Missing Africa's Talking username"


    if not AFRICAS_TALKING_API_KEY:
        return "Missing Africa's Talking API key"


    if not isinstance(
        phone_number,
        str,
    ) or not phone_number.strip():

        return "Invalid phone number"



    if not isinstance(
        message,
        str,
    ) or not message.strip():

        return "Invalid message"



    return None





def _parse_json_response(
    body: str,
):

    if not body:
        return None


    try:

        return json.loads(body)


    except json.JSONDecodeError:

        return {
            "raw_response": body
        }





def _validate_provider_response(
    provider_response: dict | None,
):

    """
    Validate Africa's Talking response.

    HTTP 201 alone does not mean
    SMS was delivered.
    """


    if not isinstance(
        provider_response,
        dict,
    ):

        return False, "Empty provider response"



    sms_data = provider_response.get(
        "SMSMessageData",
        {}
    )



    recipients = sms_data.get(
        "Recipients",
        []
    )



    if not recipients:

        return False, sms_data.get(
            "Message",
            "No recipients accepted"
        )



    for recipient in recipients:


        if recipient.get(
            "status"
        ) == "Success":

            return True, None



    return False, "SMS delivery failed"




# ============================================================
# SEND SMS
# ============================================================


def send_sms(
    phone_number: str,
    message: str,
) -> dict:


    validation_error = _validate_input(

        phone_number,

        message,

    )


    if validation_error:

        return {

            "success": False,

            "stage":
                "validation",

            "error":
                validation_error,

        }



    payload = {


        "username":
            AFRICAS_TALKING_USERNAME,


        "to":
            phone_number,


        "message":
            message,

    }



    if AFRICAS_TALKING_SENDER_ID:

        payload["from"] = (

            AFRICAS_TALKING_SENDER_ID

        )



    encoded_payload = urllib.parse.urlencode(

        payload

    ).encode(

        "utf-8"

    )



    request = urllib.request.Request(

        AFRICAS_TALKING_SMS_URL,

        data=encoded_payload,

        headers={

            "apiKey":
                AFRICAS_TALKING_API_KEY,


            "Accept":
                "application/json",


            "Content-Type":
                "application/x-www-form-urlencoded",


            "User-Agent":
                "MONJED-AI-SMS-Service",

        },

        method="POST",

    )


    try:

        with urllib.request.urlopen(

            request,

            timeout=REQUEST_TIMEOUT_SECONDS,

        ) as response:


            body = response.read().decode(
                "utf-8"
            )


            provider_response = _parse_json_response(
                body
            )



            delivered, error = _validate_provider_response(

                provider_response

            )



            return {


                "success":
                    delivered,


                "status_code":
                    response.status,


                "provider":
                    "AFRICAS_TALKING",


                "phone":
                    phone_number,


                "response":
                    provider_response,


                **(

                    {

                        "error":
                            error,

                        "stage":
                            "provider",

                    }

                    if not delivered

                    else {}

                ),

            }



    except urllib.error.HTTPError as error:


        body = error.read().decode(
            "utf-8"
        )


        return {


            "success": False,


            "stage":
                "http_error",


            "status_code":
                error.code,


            "provider":
                "AFRICAS_TALKING",


            "error":
                _parse_json_response(body),

        }



    except urllib.error.URLError as error:


        return {


            "success": False,


            "stage":
                "connection",


            "provider":
                "AFRICAS_TALKING",


            "error":
                str(error.reason),

        }



    except Exception as error:


        return {


            "success": False,


            "stage":
                "unknown",


            "provider":
                "AFRICAS_TALKING",


            "error":
                str(error),

        }