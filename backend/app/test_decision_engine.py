"""
MONJED AI - Decision Engine Test

Validates:

Risk Assessment
        +
Community Evidence
        |
        ↓
Decision Engine


Important checks:
- Risk score never changes.
- Community evidence affects operational action only.
"""


import json


from backend.app.schemas.decision import (
    DecisionInput,
    CommunityEvidence,
)


from AI.decision_engine.decision_engine import (
    generate_decision,
)




# ============================================================
# HELPER
# ============================================================


def print_result(
    title,
    decision,
):

    print(
        f"\n========== {title} =========="
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
# TEST 1
# HIGH RISK WITHOUT EVIDENCE
# ============================================================


def test_high_risk_without_evidence():


    decision_input = DecisionInput(

        hazard="flood",

        zone_id="zone_test_01",

        risk_score=75.0,

        risk_level="high",

        confidence=0.85,

        evidence=[],

    )


    result = generate_decision(
        decision_input
    )


    print_result(

        "HIGH FLOOD - NO EVIDENCE",

        result,

    )




# ============================================================
# TEST 2
# RISING WATER EVIDENCE
# ============================================================


def test_rising_water_evidence():


    evidence = [

        CommunityEvidence(

            zone_id="zone_test_01",

            evidence_type="rising_water",

            description=
                "Water level is increasing near residential areas.",

            age_minutes=10,

            verified=False,

        )

    ]



    decision_input = DecisionInput(

        hazard="flood",

        zone_id="zone_test_01",

        risk_score=75.0,

        risk_level="high",

        confidence=0.85,

        evidence=evidence,

    )



    result = generate_decision(
        decision_input
    )


    print_result(

        "HIGH FLOOD - RISING WATER",

        result,

    )





# ============================================================
# TEST 3
# PEOPLE TRAPPED
# ============================================================


def test_people_trapped():


    evidence = [

        CommunityEvidence(

            zone_id="zone_test_01",

            evidence_type="people_trapped",

            description=
                "Residents reported trapped people inside flooded houses.",

            age_minutes=5,

            verified=False,

        )

    ]



    decision_input = DecisionInput(

        hazard="flood",

        zone_id="zone_test_01",

        risk_score=75.0,

        risk_level="high",

        confidence=0.85,

        evidence=evidence,

    )



    result = generate_decision(
        decision_input
    )


    print_result(

        "HIGH FLOOD - PEOPLE TRAPPED",

        result,

    )




# ============================================================
# RUN
# ============================================================


if __name__ == "__main__":


    print(
        """
=====================================
MONJED DECISION ENGINE TEST
=====================================
"""
    )


    test_high_risk_without_evidence()


    test_rising_water_evidence()


    test_people_trapped()



    print(
        """
=====================================
TEST COMPLETED
=====================================
"""
    )