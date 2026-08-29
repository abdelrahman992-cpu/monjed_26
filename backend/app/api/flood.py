from fastapi import APIRouter

from app.schemas.flood import FloodRiskInput, FloodRiskResult
from app.engines.flood_risk_engine import calculate_flood_risk


router = APIRouter(
    prefix="/api/flood",
    tags=["Flood Risk"]
)


@router.post("/risk", response_model=FloodRiskResult)
def assess_flood_risk(data: FloodRiskInput):
    return calculate_flood_risk(data)