from datetime import datetime, timezone

from fastapi import APIRouter

from app.schemas.risk import EarthquakeRiskInput, RiskAssessment
from app.services.earthquake_risk import calculate_earthquake_risk
from app.services.action_engine import get_earthquake_actions


router = APIRouter(
    prefix="/risk",
    tags=["Earthquake Risk"],
)


@router.post(
    "/earthquake",
    response_model=RiskAssessment,
)
def assess_earthquake_risk(
    data: EarthquakeRiskInput,
) -> RiskAssessment:

    score, level, reasons, confidence = calculate_earthquake_risk(data)

    actions = get_earthquake_actions(level)

    return RiskAssessment(
        hazard="earthquake",
        zone_id=data.zone_id,
        risk_score=score,
        risk_level=level,
        confidence=confidence,
        reasons=reasons,
        current_action=actions["current"],
        backup_action=actions["backup"],
        evaluated_at=datetime.now(timezone.utc),
    )