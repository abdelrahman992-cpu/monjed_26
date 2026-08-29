from app.schemas.accessibility import (
    AccessibilityProfile,
    AccessibleActionPlan,
)

from app.schemas.decision import FinalDecision


# ============================================================
# HELPERS
# ============================================================

def _append_action(
    base_action: str,
    additional_instruction: str,
) -> str:
    """
    Safely append an accessibility instruction to an
    existing backend-approved action.
    """

    base_action = base_action.strip()
    additional_instruction = additional_instruction.strip()

    if not additional_instruction:
        return base_action

    if not base_action:
        return additional_instruction

    return (
        f"{base_action} "
        f"{additional_instruction}"
    )


# ============================================================
# ACCESSIBILITY ADAPTER
# ============================================================

def adapt_decision_for_accessibility(
    decision: FinalDecision,
    profile: AccessibilityProfile,
) -> AccessibleActionPlan:
    """
    Adapt MONJED's deterministic operational decision
    for accessibility needs.

    IMPORTANT:
    - This layer does NOT modify risk_score.
    - This layer does NOT modify risk_level.
    - This layer does NOT change decision_status.
    - It does NOT override the Decision Engine.
    - It only adapts backend-approved actions and
      communication requirements.

    Safety priority:
    human_review_required always takes priority over
    normal mobility movement guidance.
    """

    needs = list(
        dict.fromkeys(
            profile.accessibility_needs
        )
    )

    adapted_current_action = (
        decision.current_action
    )

    adapted_backup_action = (
        decision.backup_action
    )

    communication_requirements: list[str] = []

    # Human-review situations already indicate that
    # trained/human assistance is required.
    assistance_required = (
        decision.decision_status
        == "human_review_required"
    )

    # ========================================================
    # 1. MOBILITY ACCESSIBILITY
    # ========================================================

    if "mobility" in needs:

        assistance_required = True

        # ----------------------------------------------------
        # SAFETY OVERRIDE
        #
        # If the Decision Engine has already escalated the
        # situation to human_review_required, do NOT add
        # autonomous movement instructions.
        # ----------------------------------------------------

        if (
            decision.decision_status
            == "human_review_required"
        ):

            adapted_current_action = _append_action(
                decision.current_action,
                (
                    "When requesting assistance, state that "
                    "mobility-accessible trained support is required."
                ),
            )

            adapted_backup_action = _append_action(
                decision.backup_action,
                (
                    "Do not attempt to move through damaged, flooded, "
                    "or otherwise unsafe areas without trained assistance."
                ),
            )

        # ----------------------------------------------------
        # FLOOD MOBILITY ADAPTATION
        # ----------------------------------------------------

        elif decision.hazard == "flood":

            adapted_current_action = _append_action(
                decision.current_action,
                (
                    "Use an accessible safe route if available. "
                    "Do not move through floodwater."
                ),
            )

            adapted_backup_action = _append_action(
                decision.backup_action,
                (
                    "If you cannot move safely, remain in the safest "
                    "accessible location available and request mobility "
                    "assistance."
                ),
            )

        # ----------------------------------------------------
        # EARTHQUAKE MOBILITY ADAPTATION
        # ----------------------------------------------------

        elif decision.hazard == "earthquake":

            adapted_current_action = _append_action(
                decision.current_action,
                (
                    "Use an accessible route only if it is safe "
                    "and not damaged."
                ),
            )

            adapted_backup_action = _append_action(
                decision.backup_action,
                (
                    "If you cannot move safely, remain in the safest "
                    "accessible location available and request trained "
                    "assistance."
                ),
            )

        communication_requirements.append(
            "Include clear information about accessible movement and assistance."
        )

    # ========================================================
    # 2. VISUAL ACCESSIBILITY
    # ========================================================

    if "visual" in needs:

        communication_requirements.extend(
            [
                "Use screen-reader-friendly text.",
                "Do not rely on colors, icons, or maps alone.",
                "Describe important directions and actions in text.",
            ]
        )

    # ========================================================
    # 3. HEARING ACCESSIBILITY
    # ========================================================

    if "hearing" in needs:

        communication_requirements.extend(
            [
                "Provide the warning in text form.",
                "Do not rely on sirens or audio alerts alone.",
                "Prefer SMS or visible digital notifications.",
            ]
        )

    # ========================================================
    # 4. COGNITIVE ACCESSIBILITY
    # ========================================================

    if "cognitive" in needs:

        communication_requirements.extend(
            [
                "Use short and simple sentences.",
                "Present actions step by step.",
                "Avoid technical jargon.",
                "Put the most important action first.",
            ]
        )

    # ========================================================
    # 5. HUMAN-REVIEW COMMUNICATION SAFETY
    # ========================================================

    if (
        decision.decision_status
        == "human_review_required"
    ):

        communication_requirements.append(
            "Make clear that trained human assistance is required."
        )

        communication_requirements.append(
            "Do not provide autonomous rescue instructions."
        )

    # ========================================================
    # 6. REMOVE DUPLICATE REQUIREMENTS
    # ========================================================

    communication_requirements = list(
        dict.fromkeys(
            communication_requirements
        )
    )

    # ========================================================
    # 7. RETURN ACCESSIBLE ACTION PLAN
    # ========================================================

    return AccessibleActionPlan(
        hazard=decision.hazard,
        zone_id=decision.zone_id,

        accessibility_needs=needs,

        original_current_action=(
            decision.current_action
        ),

        original_backup_action=(
            decision.backup_action
        ),

        adapted_current_action=(
            adapted_current_action
        ),

        adapted_backup_action=(
            adapted_backup_action
        ),

        communication_requirements=(
            communication_requirements
        ),

        assistance_request_recommended=(
            assistance_required
        ),
    )