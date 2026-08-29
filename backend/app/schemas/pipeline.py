from pydantic import BaseModel

from app.schemas.risk import RiskAssessment
from app.schemas.decision import FinalDecision
from app.schemas.accessibility import AccessibleActionPlan
from app.schemas.assistance import AssistanceRequestRecord


class MonjedAssessment(BaseModel):
    """
    Final response model returned by the MONJED pipeline.

    This schema represents the completed assessment only.
    It does not perform persistence, risk calculation,
    decision-making, or alert generation.
    """

    risk: RiskAssessment

    decision: FinalDecision

    accessible_action: AccessibleActionPlan | None = None

    assistance_request: AssistanceRequestRecord | None = None

    ai_alert: dict | None = None

    # SMS / dashboard delivery summary for ops UI.
    delivery: dict | None = None
