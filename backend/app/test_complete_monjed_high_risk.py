"""
MONJED AI - High Risk End-to-End Test

Scenario:
    High Flood Risk
        +
    No Community Evidence

Expected:
    Risk level:
        high

    Decision:
        action_adjusted

    Notification:
        True

    Delivery:
        Dashboard
        SMS attempt when recipient exists
        Voice simulation

Purpose:
    Validate the MONJED high-risk pipeline from
    deterministic risk input through decision,
    AI communication, normalization, and delivery.

IMPORTANT:
- Risk is simulated only to guarantee a high-risk scenario.
- Decision logic is real.
- AI communication pipeline is real.
- Deterministic fallback is allowed.
- Voice currently uses MOCK_TTS.
"""


import json

from types import SimpleNamespace


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
# TEST CONFIGURATION
# ============================================================


ZONE_ID = "zone_test_01"

LANGUAGE = "en"

TEST_SMS_RECIPIENTS = [
    "+20XXXXXXXXXX",
]


# ============================================================
# PRINT HELPER
# ============================================================


def print_json_section(
    title: str,
    data,
) -> None:
    """
    Print test output in a consistent readable format.
    """

    print(
        f"\n========== {title} =========="
    )

    print(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    )


# ============================================================
# 1. SIMULATED HIGH-RISK BACKEND RESULT
# ============================================================


risk = {

    "hazard":
        "flood",

    "country":
        "Kenya",

    "risk_score":
        75.0,

    "risk_level":
        "high",

    "confidence":
        0.85,

    "reasons": [
        (
            "Heavy rainfall detected and "
            "water levels are increasing."
        )
    ],
}


print_json_section(
    "HIGH RISK INPUT",
    risk,
)


# ============================================================
# 2. DECISION ENGINE
# ============================================================


decision_input = DecisionInput(

    hazard=
        risk["hazard"],

    zone_id=
        ZONE_ID,

    risk_score=
        risk["risk_score"],

    risk_level=
        risk["risk_level"],

    confidence=
        risk["confidence"],

    evidence=[],
)


decision = generate_decision(
    decision_input
)


decision_data = decision.model_dump()


print_json_section(
    "DECISION",
    decision_data,
)


# ============================================================
# DECISION VALIDATION
# ============================================================


assert decision.risk_score == risk["risk_score"], (
    "Decision Engine modified risk_score."
)


assert decision.risk_level == risk["risk_level"], (
    "Decision Engine modified risk_level."
)


assert decision.confidence == risk["confidence"], (
    "Decision Engine modified confidence."
)


assert decision.evidence_used == 0, (
    "Expected zero community evidence items."
)


assert decision.decision_status == "action_adjusted", (
    "Expected action_adjusted for high-risk scenario."
)


assert decision.notification_required is True, (
    "High-risk scenario should require notification."
)


# ============================================================
# 3. BACKEND ASSESSMENT FOR AI ADAPTER
# ============================================================
#
# SimpleNamespace is used because the AI Adapter expects
# attribute-based objects:
#
#     assessment.risk.risk_score
#     assessment.risk.confidence
#     assessment.decision
#
# ============================================================


backend_risk = SimpleNamespace(

    zone_id=
        decision.zone_id,

    country=
        risk["country"],

    hazard=
        risk["hazard"],

    risk_score=
        risk["risk_score"],

    risk_level=
        risk["risk_level"],

    confidence=
        risk["confidence"],

    reasons=
        risk["reasons"],
)


assessment = SimpleNamespace(

    risk=
        backend_risk,

    decision=
        decision,

    country=
        risk["country"],
)


# ============================================================
# ASSESSMENT VALIDATION
# ============================================================


assert assessment.risk.confidence == 0.85, (
    "Risk confidence was lost while building "
    "the backend assessment object."
)


# ============================================================
# 4. AI COMMUNICATION PIPELINE
# ============================================================


pipeline_result = run_ai_pipeline(

    assessment,

    accessibility=None,

    language=LANGUAGE,
)


payload = pipeline_result[
    "payload"
]


ai_alert = pipeline_result[
    "alert"
]


# ============================================================
# AI PAYLOAD VALIDATION
# ============================================================


payload_hazards = payload.get(
    "hazards",
    [],
)


assert payload_hazards, (
    "AI payload contains no hazards."
)


payload_hazard = payload_hazards[0]


assert payload_hazard.get(
    "risk_score"
) == risk["risk_score"], (
    "AI Adapter changed risk_score."
)


assert payload_hazard.get(
    "risk_level"
) == risk["risk_level"], (
    "AI Adapter changed risk_level."
)


assert payload_hazard.get(
    "confidence"
) == risk["confidence"], (
    "AI Adapter lost or changed confidence."
)


assert payload.get(
    "decision",
    {},
).get(
    "notification_required"
) is True, (
    "AI payload lost notification_required."
)


print_json_section(
    "AI PAYLOAD",
    payload,
)


print_json_section(
    "AI ALERT",
    ai_alert,
)


# ============================================================
# 5. NORMALIZE ALERT
# ============================================================


normalized_alert = normalize_alert(

    ai_alert,

    payload,
)


# ============================================================
# NORMALIZED ALERT VALIDATION
# ============================================================


normalized_hazards = normalized_alert.get(
    "hazards",
    [],
)


assert normalized_hazards, (
    "Normalized alert contains no hazards."
)


normalized_hazard = normalized_hazards[0]


assert normalized_hazard.get(
    "risk_score"
) == risk["risk_score"], (
    "Alert Normalizer changed risk_score."
)


assert normalized_hazard.get(
    "risk_level"
) == risk["risk_level"], (
    "Alert Normalizer changed risk_level."
)


assert normalized_hazard.get(
    "confidence"
) == risk["confidence"], (
    "Alert Normalizer lost or changed confidence."
)


assert normalized_alert.get(
    "notification_required"
) is True, (
    "Normalized alert lost notification_required."
)


normalized_decision = normalized_alert.get(
    "final_decision",
    {},
)


assert normalized_decision.get(
    "notification_required"
) is True, (
    "Final normalized decision lost "
    "notification_required."
)


assert normalized_decision.get(
    "current_action"
) == payload["decision"]["current_action"], (
    "Alert Normalizer modified current_action."
)


assert normalized_decision.get(
    "backup_action"
) == payload["decision"]["backup_action"], (
    "Alert Normalizer modified backup_action."
)


print_json_section(
    "NORMALIZED ALERT",
    normalized_alert,
)


# ============================================================
# 6. DISPATCH
# ============================================================
#
# Placeholder number is intentionally used here.
#
# Africa's Talking may return InvalidPhoneNumber.
# That does NOT invalidate the MONJED pipeline test.
#
# Real SMS delivery is tested separately using the
# dedicated SMS integration/provider test.
# ============================================================


dispatch_result = dispatch_alert(

    normalized_alert,

    sms_recipients=
        TEST_SMS_RECIPIENTS,
)


print_json_section(
    "DISPATCH RESULT",
    dispatch_result,
)


# ============================================================
# DISPATCH VALIDATION
# ============================================================


assert dispatch_result.get(
    "notification_required"
) is True, (
    "Dispatcher lost notification_required."
)


assert dispatch_result.get(
    "dashboard"
), (
    "Dashboard output was not generated."
)


voice_result = dispatch_result.get(
    "voice",
    {},
)


assert voice_result.get(
    "success"
) is True, (
    "Voice pipeline failed."
)


assert voice_result.get(
    "provider"
) == "MOCK_TTS", (
    "Unexpected voice provider during test."
)


assert voice_result.get(
    "delivery_status"
) == "simulated", (
    "Voice result should be marked as simulated."
)


# ============================================================
# FINAL RESULT
# ============================================================


print(
    "\n"
    "============================================\n"
    "MONJED HIGH-RISK E2E TEST PASSED\n"
    "============================================"
)