"""
MONJED AI - Complete End To End Test

Flow:

NASA / USGS
      |
      ↓
Risk Service
      |
      ↓
Decision Engine
      |
      ↓
AI Pipeline
      |
      ↓
Alert Normalizer
      |
      ↓
Dispatcher
      |
      ↓
SMS / Voice
"""


import json



from backend.app.services.risk_service import (
    run_risk_assessment,
)


from backend.app.schemas.decision import (
    DecisionInput,
)


from AI.decision_engine.decision_engine import (
    generate_decision,
)


from AI.ai_alert.integration import (
    run_ai_pipeline,
)


from backend.app.services.alert_normalizer import (
    normalize_alert,
)


from backend.app.services.alert_dispatcher import (
    dispatch_alert,
)




# ============================================================
# 1. RISK ENGINE + RISK SERVICE
# ============================================================


risk_result = run_risk_assessment(

    hazard="flood",

    country="Kenya",

    language="en",

)



print(
    "\n========== RISK RESULT =========="
)


print(

    json.dumps(

        risk_result,

        indent=2,

        ensure_ascii=False,

    )

)



risk = risk_result["risk"]




# ============================================================
# 2. DECISION ENGINE
# ============================================================


decision_input = DecisionInput(

    hazard=risk["hazard"],

    zone_id="zone_test_01",

    risk_score=risk["risk_score"],

    risk_level=risk["risk_level"],

    confidence=risk["confidence"],

    evidence=[],

)



decision = generate_decision(

    decision_input

)



print(
    "\n========== DECISION =========="
)


print(

    json.dumps(

        decision.model_dump(),

        indent=2,

        ensure_ascii=False,

        default=str,

    )

)




# ============================================================
# 3. CREATE BACKEND ASSESSMENT OBJECT
# ============================================================


class RiskObject:

    pass



class AssessmentObject:

    pass



backend_risk = RiskObject()


backend_risk.zone_id = decision.zone_id

backend_risk.country = risk["country"]

backend_risk.hazard = risk["hazard"]

backend_risk.risk_score = risk["risk_score"]

backend_risk.risk_level = risk["risk_level"]

backend_risk.reasons = risk["reasons"]



assessment = AssessmentObject()


assessment.risk = backend_risk

assessment.decision = decision




# ============================================================
# 4. AI PIPELINE
# ============================================================


pipeline_result = run_ai_pipeline(

    assessment,

    accessibility=None,

    language="en",

)



ai_alert = pipeline_result["alert"]



print(
    "\n========== AI ALERT =========="
)


print(

    json.dumps(

        ai_alert,

        indent=2,

        ensure_ascii=False,

        default=str,

    )

)




# ============================================================
# 5. NORMALIZE
# ============================================================


normalized_alert = normalize_alert(

    ai_alert,

    pipeline_result["payload"],

)



print(
    "\n========== NORMALIZED ALERT =========="
)


print(

    json.dumps(

        normalized_alert,

        indent=2,

        ensure_ascii=False,

        default=str,

    )

)




# ============================================================
# 6. DELIVERY
# ============================================================


dispatch_result = dispatch_alert(

    normalized_alert,

    sms_recipients=[

        "+20XXXXXXXXXX"

    ],

)



print(
    "\n========== DISPATCH RESULT =========="
)


print(

    json.dumps(

        dispatch_result,

        indent=2,

        ensure_ascii=False,

        default=str,

    )

)