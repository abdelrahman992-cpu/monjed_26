from enum import Enum
from pydantic import BaseModel, Field


class RainfallTrend(str, Enum):
    increasing = "increasing"
    stable = "stable"
    decreasing = "decreasing"


class RiskLevel(str, Enum):
    low = "low"
    moderate = "moderate"
    high = "high"
    critical = "critical"


class FloodRiskInput(BaseModel):
    rainfall_mm: float = Field(
        ...,
        ge=0,
        description="Recent rainfall amount in millimeters"
    )

    soil_moisture: float = Field(
        ...,
        ge=0,
        le=1,
        description="Soil moisture value between 0 and 1"
    )

    rainfall_trend: RainfallTrend


class FloodRiskResult(BaseModel):
    risk_score: float = Field(
        ...,
        ge=0,
        le=100
    )

    risk_level: RiskLevel

    reasons: list[str]