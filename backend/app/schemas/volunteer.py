from typing import Literal

from pydantic import BaseModel, Field


# ============================================================
# TYPES
# ============================================================

VolunteerSkill = Literal[
    "evacuation",
    "transportation",
    "mobility_assistance",
    "medical_support",
    "rescue_support",
    "general_support",
]


ResponderLevel = Literal[
    "volunteer",
    "trained_responder",
]



# ============================================================
# INPUT
# ============================================================

class VolunteerInput(BaseModel):

    """
    Volunteer or trained responder profile.

    GPS is used only for ranking qualified responders.
    Qualification is handled separately by matching engine.
    """

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )


    zone_id: str = Field(
        ...,
        min_length=1,
    )



    # --------------------------------------------------------
    # GPS
    # --------------------------------------------------------

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



    available: bool = True



    # --------------------------------------------------------
    # Safety level
    # --------------------------------------------------------

    responder_level: ResponderLevel = (
        "volunteer"
    )



    # --------------------------------------------------------
    # Transport
    # --------------------------------------------------------

    vehicle_type: str | None = Field(
        default=None,
        max_length=100,
    )


    capacity: int = Field(
        default=1,
        ge=1,
        le=100,
    )



    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    skills: list[VolunteerSkill] = Field(
        default_factory=list
    )



# ============================================================
# STORED
# ============================================================

class VolunteerRecord(
    VolunteerInput
):

    volunteer_id: str


# ============================================================
# UPDATE
# ============================================================

class VolunteerAvailabilityUpdate(BaseModel):
    """
    Frontend-safe volunteer availability update.

    Operational qualifications, responder level, skills,
    and identity are not modified through this endpoint.
    """

    available: bool
