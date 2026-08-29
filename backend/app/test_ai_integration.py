from AI.ai_alert.integration import run_ai_pipeline



# ============================================================
# MOCK BACKEND MODELS
# Matches ai_adapter.py contract
# ============================================================


class MockRisk:

    def __init__(self):

        self.zone_id = "zone_test_01"

        self.country = "Kenya"

        self.hazard = "flood"

        self.risk_score = 82

        self.risk_level = "high"

        self.reasons = [

            "Heavy rainfall detected and water levels are increasing."

        ]



class MockDecision:

    def __init__(self):

        self.decision_status = (
            "action_adjusted"
        )

        self.current_action = (
            "Move to a safer elevated area immediately."
        )

        self.backup_action = (
            "Avoid flooded roads and do not cross moving water."
        )

        self.evidence_used = 3



class MockAssessment:

    def __init__(self):

        self.risk = MockRisk()

        self.decision = MockDecision()

        self.country = "Kenya"



class MockAccessibility:

    def __init__(self):

        self.accessibility_needs = [

            "mobility"

        ]


        self.communication_requirements = [

            "Assist people with mobility difficulties."

        ]


        self.adapted_current_action = (

            "Move to a safer elevated area immediately. "
            "Assist people with mobility difficulties."

        )


        self.adapted_backup_action = (

            "Avoid flooded roads and do not cross moving water."

        )



# ============================================================
# RUN TEST
# ============================================================


assessment = MockAssessment()

accessibility = MockAccessibility()



result = run_ai_pipeline(

    assessment,

    accessibility=accessibility,

    language="sw"

)



print(
    "\n========== FINAL RESULT =========="
)


print(result)