import json


from AI.ai_alert.gemini_alert import (
    generate_alert,
    validate_alert,
)


# ============================================================
# MONJED AI TEST PAYLOAD
# HIGH EARTHQUAKE + ACCESSIBILITY
# ============================================================


monjed_payload = {

    "zone_id":
        "test_eq_rescue_01",

    "country":
        "Egypt",

    "language":
        "en",


    "hazards": [

        {

            "hazard":
                "earthquake",

            "risk_score":
                73,

            "risk_level":
                "high",

            "confidence":
                0.9,

            "reasons":
                [
                    "Strong earthquake magnitude",
                    "Shallow earthquake depth",
                ],
        }
    ],


    "community_evidence":

        {
            "matching_reports":
                2
        },


    "decision":

        {

            "decision_status":
                "human_review_required",


            "current_action":
                "Request emergency or trained human assistance.",


            "backup_action":
                "Do not attempt unsafe rescue actions.",


            "accessibility_instructions":
                [
                    "Request mobility-accessible assistance."
                ],
        },


    "accessibility_needs":

        [
            "mobility"
        ],
}



# ============================================================
# 1. GENERATE ALERT
# ============================================================


print(
    "\n========== GENERATE ALERT ==========\n"
)


alert = generate_alert(
    monjed_payload
)


print(
    json.dumps(
        alert,
        indent=2,
        ensure_ascii=False
    )
)



# ============================================================
# 2. NORMAL VALIDATION
# ============================================================


print(
    "\n========== NORMAL VALIDATION ==========\n"
)


normal_validation = validate_alert(
    monjed_payload,
    alert,
)


print(
    json.dumps(
        normal_validation,
        indent=2
    )
)



# ============================================================
# 3. ATTACK TEST
# ============================================================


print(
    "\n========== ATTACK TEST ==========\n"
)


tampered_alert = alert.copy()


# AI tries to reduce risk level

tampered_alert["hazards"][0]["risk_score"] = 20


attack_validation = validate_alert(
    monjed_payload,
    tampered_alert,
)


print(
    json.dumps(
        attack_validation,
        indent=2
    )
)



# ============================================================
# RESULT
# ============================================================


print(
    "\n========== RESULT ==========\n"
)


if normal_validation["valid"]:

    print(
        "PASS: Valid MONJED AI alert accepted."
    )

else:

    print(
        "FAIL: Valid alert rejected."
    )



if not attack_validation["valid"]:

    print(
        "PASS: Modified AI output rejected."
    )

else:

    print(
        "FAIL: Modified AI output accepted."
    )