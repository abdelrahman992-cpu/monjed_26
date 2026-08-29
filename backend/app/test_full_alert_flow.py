"""
MONJED Full Alert Pipeline Test

Flow:

AI Adapter Payload
        |
        ↓
Gemini Alert Layer
        |
        ↓
Alert Normalizer
        |
        ↓
Alert Dispatcher
        |
        ↓
Africa's Talking SMS
"""


from backend.app.services.gemini_alert import generate_alert

from backend.app.services.alert_normalizer import normalize_alert

from backend.app.services.alert_dispatcher import dispatch_alert

# ============================================================
# MOCK BACKEND APPROVED PAYLOAD
# ============================================================

backend_payload = {


    "source":
        "MONJED_BACKEND",


    "ai_role":
        "communication_only",


    "zone_id":
        "zone_test_01",


    "country":
        "Kenya",


    "language":
        "sw",



    "hazards":

        [

            {

                "hazard":
                    "flood",

                "risk_score":
                    82,

                "risk_level":
                    "high",

                "reasons":

                    [
                        "Heavy rainfall detected and water levels are increasing."
                    ],

            }

        ],



    "community_evidence":

        {

            "matching_reports":
                3

        },



    "decision":

        {

            "decision_status":
                "action_adjusted",


            "current_action":

                "Move to a safer elevated area immediately.",


            "backup_action":

                "Avoid flooded roads and do not cross moving water.",


            "accessibility_instructions":

                [

                    "Assist people with mobility difficulties.",

                ],

        },



    "accessibility_needs":

        [

            "mobility"

        ]

}





# ============================================================
# RUN TEST
# ============================================================


if __name__ == "__main__":


    print(
        "\n========== 1. GEMINI ALERT ==========\n"
    )


    ai_alert = generate_alert(
        backend_payload
    )


    print(
        ai_alert
    )



    print(
        "\n========== 2. NORMALIZED ALERT ==========\n"
    )


    normalized_alert = normalize_alert(

        ai_alert,

        backend_payload,

    )


    print(
        normalized_alert
    )



    print(
        "\n========== 3. DISPATCH ==========\n"
    )


    result = dispatch_alert(

        normalized_alert,


        sms_recipients=[

            "+20XXXXXXXXXX"

        ],

    )


    print(
        result
    )