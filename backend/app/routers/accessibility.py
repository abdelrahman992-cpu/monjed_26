from fastapi import APIRouter

from app.schemas.accessibility import (
    AccessibilityDecisionInput,
    AccessibleActionPlan,
)

from app.services.accessibility_adapter import (
    adapt_decision_for_accessibility,
)


router = APIRouter(
    prefix="/accessibility",
    tags=["Accessibility"],
)


@router.post(
    "/adapt",
    response_model=AccessibleActionPlan,
)
def adapt_accessibility(
    data: AccessibilityDecisionInput,
):

    return adapt_decision_for_accessibility(
        decision=data.decision,
        profile=data.profile,
    )