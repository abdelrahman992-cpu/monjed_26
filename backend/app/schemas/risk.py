from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


RiskLevel = Literal[
    "low",
    "moderate",
    "high",
    "critical",
]

HazardType = Literal[
    "flood",
    "earthquake",
]


class FloodRiskInput(BaseModel):
    zone_id: str = Field(
        min_length=1
    )

    rainfall_1h_mm: float = Field(
        ge=0
    )

    rainfall_24h_mm: float = Field(
        ge=0
    )

    previous_rainfall_24h_mm: float | None = Field(
        default=None,
        ge=0
    )

    data_age_minutes: int = Field(
        default=0,
        ge=0
    )


class EarthquakeRiskInput(BaseModel):
    zone_id: str = Field(
        min_length=1
    )

    magnitude: float = Field(
        ge=0
    )

    depth_km: float = Field(
        ge=0
    )

    distance_km: float = Field(
        ge=0
    )

    data_age_minutes: int = Field(
        default=0,
        ge=0
    )

    source_verified: bool = True


class RiskAssessment(BaseModel):
    hazard: HazardType

    zone_id: str

    risk_score: int = Field(
        ge=0,
        le=100
    )

    risk_level: RiskLevel

    confidence: float = Field(
        ge=0,
        le=1
    )

    reasons: list[str]

    evaluated_at: datetime