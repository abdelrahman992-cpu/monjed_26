"""
MONJED SMS End-to-End Flow Test

Flow:

MONJED Alert
      |
      ↓
SMS Service
      |
      ↓
SMS Formatter
      |
      ↓
Africa's Talking
      |
      ↓
Real SMS


This simulates the output
coming from Alert Normalizer.
"""


import json



from backend.app.services.sms.sms_service import (
    send_alert_sms,
)



# ============================================================
# SIMULATED NORMALIZED MONJED ALERT
# ============================================================

monjed_alert = {


    "title":
        "MONJED Alert",


    "country":
        "Kenya",


    "zone_id":
        "Zone Test 01",


    "language":
        "en",



    "hazards":

        [

            {

                "type":
                    "flood",


                "risk_score":
                    75,


                "risk_level":
                    "high",

            }

        ],



    "final_decision":

        {


            "decision_status":
                "action_adjusted",



            "current_action":

                "Move to a safer elevated area immediately.",



            "backup_action":

                "Avoid flooded roads and do not cross moving water.",


        },


}



# ============================================================
# SEND MONJED GENERATED SMS
# ============================================================


print(
    "\n====================================="
)

print(
    "MONJED SMS FLOW TEST"
)

print(
    "=====================================\n"
)



print(
    "NORMALIZED ALERT:"
)


print(

    json.dumps(

        monjed_alert,

        indent=2,

        ensure_ascii=False,

    )

)



result = send_alert_sms(

    "+20xxxxxxxxxx",

    monjed_alert,

)



print(
    "\n====================================="
)

print(
    "SMS RESULT"
)

print(
    "=====================================\n"
)



print(

    json.dumps(

        result,

        indent=2,

        ensure_ascii=False,

        default=str,

    )

)