from backend.app.services.sms.sms_formatter import (
    format_sms_alert
)


alert = {

    "language": "sw",

    "country": "Kenya",

    "hazards": [

        {
            "type": "flood",
            "risk_level": "high",
            "risk_score": 82
        }

    ],

    "final_decision": {

        "current_action":
            "Move to a safer elevated area immediately.",

        "backup_action":
            "Avoid flooded roads and do not cross moving water."

    },

    "accessibility_needs":

        [
            "mobility"
        ]

}


message = format_sms_alert(
    alert
)


print(message)