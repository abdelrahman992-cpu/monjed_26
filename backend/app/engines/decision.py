from datetime import datetime, timezone

from app.schemas.decision import DecisionInput


# ============================================================
# CONSTANTS
# ============================================================

SUPPORTED_HAZARDS = {
    "flood",
    "earthquake",
}

ACTIVE_NOTIFICATION_RISK_LEVELS = {
    "high",
    "critical",
}

ACTION_ADJUSTMENT_STATUSES = {
    "action_adjusted",
    "human_review_required",
}


# ============================================================
# BASELINE FLOOD ACTIONS
# ============================================================

def _get_flood_base_actions(
    risk_level: str,
) -> tuple[str, str]:
    """
    Return deterministic baseline flood safety actions
    based only on the backend scientific risk level.

    MONJED provides a direct action first.
    Official updates may support the action,
    but they do not replace it.
    """

    if risk_level == "critical":
        return (
            "Move away from flood-prone and low-lying areas "
            "and relocate to a safer elevated location if it "
            "is safe to do so.",
            "Do not walk or drive through floodwater. If safe "
            "movement is not possible, remain in the safest "
            "available elevated location and request assistance.",
        )

    if risk_level == "high":
        return (
            "Stay away from low-lying areas and floodwater, "
            "and prepare to move to a safer elevated location "
            "before conditions become more dangerous.",
            "Do not enter flooded roads or moving water. If "
            "water begins rising around you, move to higher "
            "ground if it is safe to do so.",
        )

    if risk_level == "moderate":
        return (
            "Avoid low-lying and flood-prone areas and keep "
            "a safe route to higher ground available.",
            "Stay away from floodwater. If water levels begin "
            "to rise or nearby routes become unsafe, move to "
            "a safer elevated location.",
        )

    return (
        "Stay away from floodwater and avoid low-lying areas "
        "where water may collect.",
        "If local water levels begin rising, move away from "
        "the affected area and use a safe route toward higher ground.",
    )


# ============================================================
# BASELINE EARTHQUAKE ACTIONS
# ============================================================

def _get_earthquake_base_actions(
    risk_level: str,
) -> tuple[str, str]:
    """
    Return deterministic post-earthquake impact actions
    based only on the backend scientific risk level.

    MONJED does not predict earthquakes.

    Immediate protective actions are prioritized before
    general monitoring guidance.
    """

    if risk_level == "critical":
        return (
            "Stay away from visibly damaged buildings, "
            "unstable structures, and falling hazards. If you "
            "are inside a damaged building and can leave safely, "
            "move outside and away from it.",
            "Do not re-enter damaged buildings. Be ready for "
            "aftershocks; if shaking starts again, Drop, Cover, "
            "and Hold On.",
        )

    if risk_level == "high":
        return (
            "Move away from visibly damaged buildings, "
            "unstable structures, and other falling hazards "
            "if it is safe to do so.",
            "Do not enter damaged structures. Be ready for "
            "aftershocks; if shaking starts again, Drop, Cover, "
            "and Hold On.",
        )

    if risk_level == "moderate":
        return (
            "Stay away from visibly damaged structures, "
            "broken glass, and other nearby hazards.",
            "Be alert for aftershocks. If shaking starts again, "
            "Drop, Cover, and Hold On.",
        )

    return (
        "Check your immediate surroundings for damage or "
        "falling hazards and stay away from any structure "
        "that appears unsafe.",
        "Be alert for aftershocks. If shaking starts again, "
        "Drop, Cover, and Hold On.",
    )


# ============================================================
# DECISION ENGINE
# ============================================================

def evaluate_decision(
    data: DecisionInput,
) -> dict:
    """
    Produce MONJED's deterministic operational decision.

    Responsibilities:
    - Preserve the backend scientific risk assessment.
    - Consider recent matching community evidence.
    - Adjust operational actions when necessary.
    - Escalate situations requiring trained human support.
    - Determine whether active notification is required.

    Community evidence does NOT modify:
    - risk_score
    - risk_level
    - confidence

    Gemini is not involved in this decision.
    """

    # ========================================================
    # 1. Validate Supported Hazard
    # ========================================================

    if data.hazard not in SUPPORTED_HAZARDS:
        raise ValueError(
            f"Unsupported hazard: {data.hazard}"
        )

    # ========================================================
    # 2. Initialize Operational Evidence State
    # ========================================================

    reasons: list[str] = []

    evidence_used = 0

    blocked_route = False
    people_trapped = False
    severe_damage = False
    rising_water = False

    # ========================================================
    # 3. Analyze Recent Community Evidence
    # ========================================================

    for report in data.evidence:

        if report.zone_id != data.zone_id:
            continue

        if report.age_minutes > 180:
            continue

        evidence_used += 1

        if report.evidence_type == "blocked_road":
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
                "people may require assistance."
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
    # 4. Baseline Operational Action
    # ========================================================

    if data.hazard == "flood":
        current_action, backup_action = _get_flood_base_actions(
            data.risk_level
        )

    elif data.hazard == "earthquake":
        current_action, backup_action = _get_earthquake_base_actions(
            data.risk_level
        )

    else:
        raise ValueError(
            f"Unsupported hazard: {data.hazard}"
        )

    decision_status = "no_adjustment"

    # ========================================================
    # 5. Scientific Risk Notification Requirement
    # ========================================================

    if data.risk_level in ACTIVE_NOTIFICATION_RISK_LEVELS:
        decision_status = "action_adjusted"

        reasons.append(
            f"Scientific risk level is {data.risk_level}; "
            "active notification is required."
        )

    # ========================================================
    # 6. Human Escalation
    # Highest Operational Priority
    # ========================================================

    if people_trapped:
        decision_status = "human_review_required"

        current_action = (
            "Request emergency or trained human assistance "
            "for the reported situation."
        )

        backup_action = (
            "Do not attempt unsafe rescue actions. Share the "
            "location and available details with responders."
        )

    # ========================================================
    # 7. Flood Operational Adjustments
    # ========================================================

    elif data.hazard == "flood":

        if severe_damage and blocked_route and rising_water:
            decision_status = "action_adjusted"

            current_action = (
                "Stay away from visibly damaged buildings or "
                "infrastructure, avoid floodwater, and do not "
                "use routes reported as blocked or flooded. "
                "Move toward a safer elevated location only "
                "if a safe route is available."
            )

            backup_action = (
                "If no safe route is confirmed, remain in the "
                "safest available elevated location away from "
                "visible structural hazards and request "
                "official assistance."
            )

        elif severe_damage and blocked_route:
            decision_status = "action_adjusted"

            current_action = (
                "Stay away from visibly damaged buildings or "
                "infrastructure and do not use routes reported "
                "as blocked or flooded."
            )

            backup_action = (
                "Remain in the safest available location until "
                "a safer route is confirmed, and request "
                "official assistance if needed."
            )

        elif severe_damage and rising_water:
            decision_status = "action_adjusted"

            current_action = (
                "Stay away from visibly damaged buildings or "
                "infrastructure, avoid floodwater, and move away "
                "from areas where water levels are rising."
            )

            backup_action = (
                "If safe movement is not possible, remain in "
                "the safest available elevated location away "
                "from visible structural hazards and request "
                "official assistance."
            )

        elif severe_damage:
            decision_status = "action_adjusted"

            current_action = (
                "Stay away from visibly damaged buildings or "
                "infrastructure and avoid nearby floodwater."
            )

            backup_action = (
                "Move to a safer location if it is safe to do "
                "so. If safe movement is not possible, remain "
                "in the safest available location and request "
                "official assistance."
            )

        elif blocked_route and rising_water:
            decision_status = "action_adjusted"

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

            current_action = (
                "Do not use routes reported as blocked or "
                "flooded. Turn back and use another route only "
                "if it is confirmed safe."
            )

            backup_action = (
                "If no safe route is confirmed, remain in the "
                "safest available location away from floodwater "
                "and request assistance."
            )

        elif rising_water:
            decision_status = "action_adjusted"

            current_action = (
                "Avoid floodwater and move away from areas "
                "where water levels are rising."
            )

            backup_action = (
                "If movement is unsafe, remain in the safest "
                "available elevated location and request "
                "assistance."
            )

    # ========================================================
    # 8. Earthquake Operational Adjustments
    # ========================================================

    elif data.hazard == "earthquake":

        if severe_damage and blocked_route:
            decision_status = "action_adjusted"

            current_action = (
                "Stay away from damaged structures and do not "
                "use routes reported as blocked or unsafe."
            )

            backup_action = (
                "Remain in the safest accessible location if "
                "you cannot leave safely. Wait for a confirmed "
                "safe route or trained assistance. If shaking "
                "starts again, Drop, Cover, and Hold On."
            )

        elif severe_damage:
            decision_status = "action_adjusted"

            current_action = (
                "Move away from visibly damaged structures "
                "and falling hazards if it is safe to do so."
            )

            backup_action = (
                "Do not re-enter damaged buildings. If shaking "
                "starts again, Drop, Cover, and Hold On."
            )

        elif blocked_route:
            decision_status = "action_adjusted"

            current_action = (
                "Do not use routes reported as blocked or "
                "unsafe. Remain on a confirmed safe route "
                "or in a safe location."
            )

            backup_action = (
                "Wait for a safer route or trained assistance "
                "rather than crossing blocked or visibly "
                "unsafe areas."
            )

    # ========================================================
    # 9. Notification Gate
    # ========================================================

    notification_required = (
        data.risk_level in ACTIVE_NOTIFICATION_RISK_LEVELS
        or decision_status in ACTION_ADJUSTMENT_STATUSES
    )

    # ========================================================
    # 10. Explanation When No Adjustment Was Needed
    # ========================================================

    if not reasons:
        reasons.append(
            "No recent community evidence required "
            "an operational action change."
        )

    # ========================================================
    # 11. Final Protected Decision
    # ========================================================

    return {
        "hazard": data.hazard,

        "zone_id": data.zone_id,

        "risk_score": data.risk_score,

        "risk_level": data.risk_level,

        "confidence": data.confidence,

        "evidence_used": evidence_used,

        "decision_status": decision_status,

        "notification_required": notification_required,

        "current_action": current_action,

        "backup_action": backup_action,

        "reasons": reasons,

        "evaluated_at": datetime.now(
            timezone.utc
        ),
    }