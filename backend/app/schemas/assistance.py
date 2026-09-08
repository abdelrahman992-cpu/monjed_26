from datetime import datetime
from typing import Literal, Optional
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
# INPUT SCHEMAS
# ============================================================

class AssistanceRequestInput(BaseModel):
    """
    Standard incoming assistance request.
    GPS is optional to enable map visualization and responder ranking.
    """
    zone_id: str = Field(..., min_length=1)
    location: str = Field(..., min_length=2)

    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)

    hazard: HazardType
    request_type: RequestType
    priority: RequestPriority

    description: str = Field(..., min_length=3, max_length=500)
    accessibility_needs: list[AccessibilityNeed] = Field(default_factory=list)
    
    requester_phone: Optional[str] = Field(
        default=None,
        min_length=7,
        max_length=20,
        description="Callback number for the volunteer or ops team.",
    )


class DistressRequest(BaseModel):
    """
    Lightweight direct distress payload for rapid guest submission.
    """
    phone: str = Field(
        ...,
        min_length=7,
        max_length=20,
        description="User phone number for distress request",
    )
    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)
    details: Optional[str] = Field(default=None, max_length=500)


# ============================================================
# STORED RECORD SCHEMA
# ============================================================

class AssistanceRequestRecord(BaseModel):
    request_id: str
    zone_id: str
    location: str

    latitude: Optional[float] = Field(default=None, ge=-90, le=90)
    longitude: Optional[float] = Field(default=None, ge=-180, le=180)

    hazard: HazardType
    request_type: RequestType
    priority: RequestPriority
    description: str
    requester_phone: Optional[str] = None

    # --------------------------------------------------------
    # Lifecycle
    # --------------------------------------------------------
    status: RequestStatus = "pending"
    assigned_volunteer_id: Optional[str] = None

    # --------------------------------------------------------
    # Traceability
    # --------------------------------------------------------
    source: AssistanceRequestSource = "manual"
    decision_status: Optional[Literal["human_review_required"]] = None
    evidence_used: int = Field(default=0, ge=0)
    source_report_ids: list[str] = Field(default_factory=list)

    # --------------------------------------------------------
    # Accessibility / Safety
    # --------------------------------------------------------
    accessibility_needs: list[AccessibilityNeed] = Field(default_factory=list)
    requires_trained_responder: bool = False

    # --------------------------------------------------------
    # Time
    # --------------------------------------------------------
    created_at: datetime
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None