"""
MONJED SMS Provider Test

Tests:
- Provider connection
- Response validation
- Failure handling
"""


import json


from backend.app.services.sms.africas_talking import (
    send_sms,
)



PHONE_NUMBER = "+20xxxxxxxxxx"



MESSAGE = """
MONJED TEST ALERT

Flood risk detected.

Action:
Move to a safer elevated area.

Safety:
Avoid flooded roads.
"""



print(
    "\n====================================="
)

print(
    "MONJED SMS PROVIDER TEST"
)

print(
    "=====================================\n"
)



result = send_sms(

    PHONE_NUMBER,

    MESSAGE,

)



print(
    json.dumps(

        result,

        indent=2,

        ensure_ascii=False,

        default=str,

    )

)