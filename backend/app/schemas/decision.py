"""
MONJED AI - Decision Models

Defines the contracts between:

Risk Engine
      |
      ↓
Decision Engine
      |
      ↓
Alert Generation


IMPORTANT:
- Community evidence influences operational decisions only.
- Community evidence NEVER modifies risk score.
- AI NEVER modifies decisions.
"""


from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    Field,
)


# ============================================================
# TYPES
# ============================================================


EvidenceType = Literal[

    "blocked_road",

    "rising_water",

    "building_damage",

    "people_trapped",

    "infrastructure_damage",

    "other",

]



RiskLevel = Literal[

    "unknown",

    "low",

    "moderate",

    "high",

    "critical",

]



HazardType = Literal[

    "flood",

    "earthquake",

]



DecisionStatus = Literal[

    "no_adjustment",

    "action_adjusted",

    "alert_required",

    "human_review_required",

]



# ============================================================
# COMMUNITY EVIDENCE
# ============================================================


class CommunityEvidence(BaseModel):
    """
    Operational evidence extracted from
    community reports.

    Evidence affects operational decisions,
    NOT scientific risk calculation.
    """


    zone_id: str = Field(
        min_length=1,
    )


    evidence_type: EvidenceType


    description: str = Field(

        min_length=3,

        max_length=500,

    )


    age_minutes: int = Field(

        ge=0,

    )


    verified: bool = False



# ============================================================
# DECISION INPUT
# ============================================================


class DecisionInput(BaseModel):
    """
    Complete input for Decision Engine.

    Combines:

    - Scientific risk assessment
    - Operational community evidence
    """


    hazard: HazardType


    zone_id: str = Field(

        min_length=1,

    )


    risk_score: float = Field(

        ge=0,

        le=100,

    )


    risk_level: RiskLevel


    confidence: float = Field(

        ge=0,

        le=1,

    )


    evidence: list[CommunityEvidence] = Field(

        default_factory=list,

    )



# ============================================================
# DECISION INPUT FROM RISK ENGINE
# ============================================================


class DecisionFromRiskInput(BaseModel):
    """
    Risk-only input.

    Community evidence is loaded separately
    using zone_id.
    """


    hazard: HazardType


    zone_id: str = Field(

        min_length=1,

    )


    risk_score: float = Field(

        ge=0,

        le=100,

    )


    risk_level: RiskLevel


    confidence: float = Field(

        ge=0,

        le=1,

    )



# ============================================================
# FINAL DECISION
# ============================================================


class FinalDecision(BaseModel):
    """
    Final deterministic operational decision.

    Produced by Decision Engine.

    Risk values are protected from:

    - community evidence
    - accessibility layer
    - AI generation

    """


    hazard: HazardType


    zone_id: str = Field(

        min_length=1,

    )


    # Original scientific assessment

    risk_score: float = Field(

        ge=0,

        le=100,

    )


    risk_level: RiskLevel


    confidence: float = Field(

        ge=0,

        le=1,

    )


        # Number of evidence items considered

    evidence_used: int = Field(

        ge=0,

    )


    decision_status: DecisionStatus


    # Whether MONJED should send active notifications
    #
    # False:
    #   Monitoring / dashboard update only
    #
    # True:
    #   SMS / Voice / Emergency channels allowed

    notification_required: bool = False



    current_action: str = Field(
    min_length=1,
)

    backup_action: str = Field(
        min_length=1,
)

    reasons: list[str] = Field(
        default_factory=list,
)

evaluated_at: datetime