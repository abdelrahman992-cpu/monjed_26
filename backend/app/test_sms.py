from backend.app.services.sms.africas_talking import send_sms


message = """
MONJED AI ALERT

FLOOD RISK DETECTED

Location:
Kenya - Zone Test 01

Risk Level:
HIGH

Immediate Action:
Move to a safer elevated area immediately.

Safety Advice:
Avoid flooded roads and do not cross moving water.

Accessibility Support:
Assist people with mobility difficulties.

Stay safe.
MONJED AI
"""


result = send_sms(
    "+20xxxxxxxxxx",
    message
)


print(result)