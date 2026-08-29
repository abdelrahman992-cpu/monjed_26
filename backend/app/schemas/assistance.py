from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field



# ============================================================
# TYPES
# ============================================================

HazardType = Literal[
    "flood",
    "earthquake",
]


RequestPriority = Literal[
    "low",
    "moderate",
    "high",
    "critical",
]


RequestStatus = Literal[
    "pending",
    "assigned",
    "in_progress",
    "resolved",
]


RequestType = Literal[
    "evacuation",
    "transportation",
    "mobility_assistance",
    "medical_support",
    "rescue_support",
    "other",
]


AssistanceRequestSource = Literal[
    "manual",
    "decision_engine",
]


AccessibilityNeed = Literal[
    "mobility",
    "visual",
    "hearing",
    "cognitive",
]



# ============================================================
# INPUT
# ============================================================

class AssistanceRequestInput(BaseModel):

    """
    Incoming assistance request.

    GPS is optional:
    - enables map visualization
    - enables nearest qualified responder ranking
    """

    zone_id: str = Field(
        ...,
        min_length=1,
    )

    location: str = Field(
        ...,
        min_length=2,
    )


    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )


    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )


    hazard: HazardType

    request_type: RequestType

    priority: RequestPriority


    description: str = Field(
        ...,
        min_length=3,
        max_length=500,
    )

    accessibility_needs: list[AccessibilityNeed] = Field(
        default_factory=list,
    )

    requester_phone: str | None = Field(
        default=None,
        min_length=7,
        max_length=20,
        description="Callback number for the volunteer or ops team.",
    )



# ============================================================
# STORED RECORD
# ============================================================

class AssistanceRequestRecord(BaseModel):

    request_id: str

    zone_id: str

    location: str


    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )


    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )


    hazard: HazardType

    request_type: RequestType

    priority: RequestPriority

    description: str

    requester_phone: str | None = None



    # --------------------------------------------------------
    # Lifecycle
    # --------------------------------------------------------

    status: RequestStatus = "pending"


    assigned_volunteer_id: str | None = None



    # --------------------------------------------------------
    # Traceability
    # --------------------------------------------------------

    source: AssistanceRequestSource = "manual"


    decision_status: Literal[
        "human_review_required"
    ] | None = None


    evidence_used: int = Field(
        default=0,
        ge=0,
    )


    source_report_ids: list[str] = Field(
        default_factory=list
    )



    # --------------------------------------------------------
    # Accessibility / Safety
    # --------------------------------------------------------

    accessibility_needs: list[
        AccessibilityNeed
    ] = Field(
        default_factory=list
    )


    requires_trained_responder: bool = False



    # --------------------------------------------------------
    # Time
    # --------------------------------------------------------

    created_at: datetime

    assigned_at: datetime | None = None

    started_at: datetime | None = None

    resolved_at: datetime | None = None