from datetime import datetime, timezone

from fastapi import APIRouter

from app.schemas.risk import (
    FloodRiskInput,
    RiskAssessment,
)

from app.services.flood_risk import calculate_flood_risk
from app.services.action_engine import get_flood_actions


router = APIRouter(
    prefix="/risk",
    tags=["Flood Risk"]
)


@router.post(
    "/flood",
    response_model=RiskAssessment
)
def assess_flood_risk(
    data: FloodRiskInput
) -> RiskAssessment:

    score, level, reasons, confidence = calculate_flood_risk(data)

    actions = get_flood_actions(level)

    return RiskAssessment(
        hazard="flood",

        zone_id=data.zone_id,

        risk_score=score,
        risk_level=level,

        confidence=confidence,

        reasons=reasons,

        current_action=actions["current"],
        backup_action=actions["backup"],

        evaluated_at=datetime.now(timezone.utc),
    )