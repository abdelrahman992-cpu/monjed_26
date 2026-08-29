"""
MONJED - Deterministic Operational Decision Engine

Responsibilities:
- Consume an already-calculated scientific risk assessment.
- Consider recent community evidence as operational evidence.
- Select the appropriate operational action.
- Decide whether an active notification is required.
- Escalate safety-critical situations to human review.

IMPORTANT SAFETY RULES:
- This engine NEVER calculates scientific risk.
- This engine NEVER changes risk_score.
- This engine NEVER changes risk_level.
- This engine NEVER changes confidence.
- Community evidence does NOT manipulate scientific risk.
- Generative AI is NOT involved in this decision.
"""

from datetime import datetime, timezone

from app.schemas.decision import DecisionInput


# ============================================================
# EVIDENCE POLICY
# ============================================================

# Only evidence that clearly requires trained / human
# intervention should trigger human review automatically.
HUMAN_REVIEW_EVIDENCE = {
    "people_trapped",
}


# Evidence that may require an operational action adjustment.
ACTION_ADJUSTMENT_EVIDENCE = {
    "blocked_road",
    "rising_water",
    "building_damage",
    "infrastructure_damage",
}


# Scientific risk levels that independently require an
# active warning, even if there are NO community reports.
ACTIVE_ALERT_RISK_LEVELS = {
    "high",
    "critical",
}


# ============================================================
# HELPERS
# ============================================================

def _has_evidence_type(
    evidence,
    evidence_types,
):
    """
    Return True when at least one community evidence item
    matches one of the requested evidence types.
    """

    return any(
        item.evidence_type in evidence_types
        for item in evidence
    )


def _evidence_types(
    evidence,
):
    """
    Return the unique evidence types while preserving order.
    """

    return list(
        dict.fromkeys(
            item.evidence_type
            for item in evidence
        )
    )


def _base_action(
    hazard,
):
    """
    Baseline monitoring action for situations that do not
    require an operational adjustment.
    """

    if hazard == "flood":
        return (
            "Monitor water levels and follow official "
            "safety guidance."
        )

    if hazard == "earthquake":
        return (
            "Stay away from potentially unsafe structures "
            "and follow official emergency guidance."
        )

    return "Follow official safety guidance."


def _high_risk_action(
    hazard,
):
    """
    Action used when scientific risk itself is high enough
    to require active notification.
    """

    if hazard == "flood":
        return (
            "Move to a safer elevated area and avoid "
            "affected locations."
        )

    if hazard == "earthquake":
        return (
            "Move to an open safe area away from damaged "
            "structures."
        )

    return (
        "Move to a safer location and follow official "
        "emergency guidance."
    )


def _community_adjusted_action(
    hazard,
    evidence_types,
):
    """
    Adapt the operational action using local community
    evidence without changing scientific risk.
    """

    evidence_types = set(
        evidence_types
    )

    if hazard == "flood":

        if "rising_water" in evidence_types:
            return (
                "Move to a safer elevated area and avoid "
                "locations where water levels are rising."
            )

        if "blocked_road" in evidence_types:
            return (
                "Avoid reported blocked roads and use only "
                "safe routes recommended by local authorities."
            )

        if (
            "building_damage" in evidence_types
            or
            "infrastructure_damage" in evidence_types
        ):
            return (
                "Avoid damaged buildings and infrastructure "
                "and move to a safer location if needed."
            )

    if hazard == "earthquake":

        if (
            "building_damage" in evidence_types
            or
            "infrastructure_damage" in evidence_types
        ):
            return (
                "Move away from damaged buildings and "
                "infrastructure and remain in a safe open area."
            )

        if "blocked_road" in evidence_types:
            return (
                "Avoid reported blocked routes and damaged "
                "areas while following official guidance."
            )

    return _high_risk_action(
        hazard
    )


# ============================================================
# MAIN DECISION ENGINE
# ============================================================

def evaluate_decision(
    data: DecisionInput,
) -> dict:
    """
    Produce MONJED's deterministic operational decision.

    Safety rules:
    - Preserve scientific risk_score exactly.
    - Preserve scientific risk_level exactly.
    - Preserve scientific confidence exactly.
    - Community evidence may adjust operational actions.
    - Community evidence may trigger human review.
    - High / critical scientific risk requires an active
      notification even without community evidence.
    - Gemini is not involved in this decision.
    """

    reasons: list[str] = []

    evidence_used = 0

    blocked_route = False
    people_trapped = False
    severe_damage = False
    rising_water = False

    # ========================================================
    # 1. ANALYZE COMMUNITY EVIDENCE
    # ========================================================

    for report in data.evidence:

        # Ignore evidence from another zone.
        if report.zone_id != data.zone_id:
            continue

        # Ignore evidence older than 3 hours.
        if report.age_minutes > 180:
            continue

        evidence_used += 1

        # IMPORTANT:
        # Community evidence does NOT modify:
        # - risk_score
        # - risk_level
        # - confidence

        if report.evidence_type in {
            "blocked_road",
            "flooded_road",
        }:
            blocked_route = True

            reason = (
                "Recent community evidence indicates "
                "a route may be unsafe."
            )

            if reason not in reasons:
                reasons.append(reason)

        elif report.evidence_type == "people_trapped":
            people_trapped = True

            reason = (
                "Recent community evidence indicates "
                "people may require trained assistance."
            )

            if reason not in reasons:
                reasons.append(reason)

        elif report.evidence_type in {
            "building_damage",
            "infrastructure_damage",
        }:
            severe_damage = True

            reason = (
                "Recent community evidence indicates "
                "structural or infrastructure damage."
            )

            if reason not in reasons:
                reasons.append(reason)

        elif report.evidence_type == "rising_water":
            rising_water = True

            reason = (
                "Recent community evidence indicates "
                "rising water levels."
            )

            if reason not in reasons:
                reasons.append(reason)

    # ========================================================
    # 2. BASELINE ACTION
    # ========================================================

    if data.hazard == "flood":

        current_action, backup_action = (
            _get_flood_base_actions(
                data.risk_level
            )
        )

    else:

        current_action, backup_action = (
            _get_earthquake_base_actions(
                data.risk_level
            )
        )

    decision_status = "no_adjustment"

    # ========================================================
    # 3. SCIENTIFIC RISK NOTIFICATION GATE
    # ========================================================

    notification_required = (
        data.risk_level
        in {
            "high",
            "critical",
        }
    )

    if notification_required:

        decision_status = "action_adjusted"

        reasons.append(
            f"Scientific risk level is {data.risk_level}; "
            "active notification is required."
        )

    # ========================================================
    # 4. HUMAN ESCALATION
    # Highest priority
    # ========================================================

    if people_trapped:

        decision_status = "human_review_required"

        notification_required = True

        current_action = (
            "Request emergency or trained human assistance "
            "for the reported situation."
        )

        backup_action = (
            "Do not attempt unsafe rescue actions. Share the "
            "location and available details with responders."
        )

        reasons.append(
            "Human review is required because people may "
            "be trapped."
        )

    # ========================================================
    # 5. FLOOD OPERATIONAL ADJUSTMENTS
    # ========================================================

    elif data.hazard == "flood":

        if blocked_route and rising_water:

            decision_status = "action_adjusted"
            notification_required = True

            current_action = (
                "Avoid floodwater and do not use routes "
                "reported as blocked or flooded. Move away "
                "from areas where water levels are rising."
            )

            backup_action = (
                "If no safe route is confirmed, remain in "
                "the safest available elevated location and "
                "request official assistance."
            )

        elif blocked_route:

            decision_status = "action_adjusted"
            notification_required = True

            current_action = (
                "Do not use routes reported as blocked or "
                "flooded. Follow verified official guidance "
                "for a safer alternative."
            )

            backup_action = (
                "If no safe route is confirmed, remain in "
                "the safest available location and request "
                "assistance."
            )

        elif rising_water:

            decision_status = "action_adjusted"
            notification_required = True

            current_action = (
                "Avoid floodwater and move away from areas "
                "where water levels are rising."
            )

            backup_action = (
                "If movement is unsafe, remain in the safest "
                "available elevated location and request "
                "assistance."
            )

        elif severe_damage:

            decision_status = "action_adjusted"
            notification_required = True

            current_action = (
                "Avoid damaged buildings or infrastructure "
                "and move to a safer location if it is safe "
                "to do so."
            )

            backup_action = (
                "Follow official emergency guidance and "
                "avoid visibly damaged areas."
            )

    # ========================================================
    # 6. EARTHQUAKE OPERATIONAL ADJUSTMENTS
    # ========================================================

    elif data.hazard == "earthquake":

        if severe_damage and blocked_route:

            decision_status = "action_adjusted"
            notification_required = True

            current_action = (
                "Avoid damaged structures and routes reported "
                "as blocked or unsafe. Follow official "
                "emergency guidance."
            )

            backup_action = (
                "Remain in the safest accessible location or "
                "move to a safer open area if it is safe to "
                "do so."
            )

        elif severe_damage:

            decision_status = "action_adjusted"
            notification_required = True

            current_action = (
                "Avoid visibly damaged structures and follow "
                "official emergency guidance."
            )

            backup_action = (
                "Move to a safer accessible open area if it "
                "is safe to do so."
            )

        elif blocked_route:

            decision_status = "action_adjusted"
            notification_required = True

            current_action = (
                "Avoid routes reported as blocked or unsafe "
                "and follow verified official guidance for "
                "a safer alternative."
            )

            backup_action = (
                "If a safe route is not confirmed, remain in "
                "the safest available location until guidance "
                "or assistance is available."
            )

    # ========================================================
    # 7. EXPLANATION
    # ========================================================

    if not reasons:

        reasons.append(
            "Scientific risk does not currently require "
            "an active notification."
        )

        reasons.append(
            "No recent community evidence required "
            "an operational action change."
        )

    if evidence_used > 0:

        reasons.append(
            f"{evidence_used} recent community evidence "
            "item(s) were considered."
        )

    # ========================================================
    # 8. FINAL PROTECTED DECISION
    # ========================================================

    return {
        "hazard":
            data.hazard,

        "zone_id":
            data.zone_id,

        "risk_score":
            data.risk_score,

        "risk_level":
            data.risk_level,

        "confidence":
            data.confidence,

        "evidence_used":
            evidence_used,

        "decision_status":
            decision_status,

        "notification_required":
            notification_required,

        "current_action":
            current_action,

        "backup_action":
            backup_action,

        "reasons":
            reasons,

        "evaluated_at":
            datetime.now(
                timezone.utc
            ),
    }