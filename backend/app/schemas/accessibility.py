from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.decision import FinalDecision


AccessibilityNeed = Literal[
    "mobility",
    "visual",
    "hearing",
    "cognitive",
]


class AccessibilityProfile(BaseModel):
    accessibility_needs: list[AccessibilityNeed] = Field(
        default_factory=list
    )


class AccessibilityDecisionInput(BaseModel):
    decision: FinalDecision
    profile: AccessibilityProfile


class AccessibleActionPlan(BaseModel):
    hazard: str
    zone_id: str

    accessibility_needs: list[AccessibilityNeed]

    original_current_action: str
    original_backup_action: str

    adapted_current_action: str
    adapted_backup_action: str

    communication_requirements: list[str]

    assistance_request_recommended: bool = False