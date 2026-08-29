from enum import Enum
from pydantic import BaseModel, Field

from app.schemas.flood import FloodRiskResult
from app.schemas.community_report import CommunityReportAnalysis


class EvidenceAgreement(str, Enum):
    low = "low"
    moderate = "moderate"
    high = "high"


class EvidenceAssessmentInput(BaseModel):
    flood_risk: FloodRiskResult
    community_evidence: CommunityReportAnalysis


class EvidenceAssessment(BaseModel):
    agreement: EvidenceAgreement

    confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description="Confidence based on agreement between available evidence sources"
    )

    situation_summary: str

    supporting_evidence: list[str]

    conflicting_evidence: list[str]

    needs_additional_verification: bool