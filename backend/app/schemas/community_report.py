from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field



# ============================================================
# ENUMS
# ============================================================

class ReportSeverity(str, Enum):

    low = "low"
    moderate = "moderate"
    high = "high"
    critical = "critical"



class HazardType(str, Enum):

    flood = "flood"
    earthquake = "earthquake"
    unknown = "unknown"



class AnalysisSource(str, Enum):

    """
    Backend mechanism used to analyze the report.

    IMPORTANT:
    This does NOT verify that the reported event is true.
    """

    GEMINI = "GEMINI"

    DETERMINISTIC_FALLBACK = (
        "DETERMINISTIC_FALLBACK"
    )



# ============================================================
# COMMUNITY REPORT INPUT
# ============================================================

class CommunityReportInput(BaseModel):

    """
    Raw community report submitted to MONJED.

    The report is analyzed before becoming
    operational evidence.
    """


    report_text: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description=(
            "Free text description of the reported situation"
        ),
    )



    zone_id: str = Field(
        ...,
        min_length=1,
        description=(
            "MONJED operational zone identifier"
        ),
    )



    location: str = Field(
        ...,
        min_length=2,
        description=(
            "Human-readable report location"
        ),
    )



    # --------------------------------------------------------
    # GPS
    # --------------------------------------------------------

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
        description=(
            "GPS latitude of reported location"
        ),
    )



    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
        description=(
            "GPS longitude of reported location"
        ),
    )



    # Optional future user/community identifier
    reporter_id: str | None = Field(
        default=None,
        min_length=1,
        description=(
            "Optional community user identifier"
        ),
    )



# ============================================================
# COMMUNITY REPORT ANALYSIS
# ============================================================

class CommunityReportAnalysis(BaseModel):

    """
    Structured evidence extracted from a report.

    IMPORTANT:

    - Represents extracted information only.
    - Does NOT mean the report is verified.
    - analysis_confidence measures extraction confidence,
      not event truth.
    """



    hazard_type: HazardType

    severity: ReportSeverity



    # --------------------------------------------------------
    # Flood Evidence
    # --------------------------------------------------------

    rising_water: bool = False

    blocked_road: bool = False



    # --------------------------------------------------------
    # Earthquake Evidence
    # --------------------------------------------------------

    building_damage: bool = False

    infrastructure_damage: bool = False



    # --------------------------------------------------------
    # Human Assistance Evidence
    # --------------------------------------------------------

    people_trapped: bool = False

    transportation_needed: bool = False

    help_needed: bool = False

    mobility_assistance_needed: bool = False



    # --------------------------------------------------------
    # AI Analysis Metadata
    # --------------------------------------------------------

    analysis_confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description=(
            "Confidence in extracting information "
            "from the submitted report."
        ),
    )



    extracted_evidence: list[str] = Field(
        default_factory=list
    )



    analysis_version: str = Field(
        default="1.0",
        description=(
            "Version of the analysis pipeline used."
        ),
    )



# ============================================================
# STORED COMMUNITY REPORT
# ============================================================

class CommunityReportRecord(BaseModel):

    """
    Persistent community report record.

    Used for:
    - MongoDB storage
    - evidence traceability
    - AI audit history
    - operations verification/resolution
    """

    report_id: str = Field(
        ...,
        min_length=1,
    )

    zone_id: str = Field(
        ...,
        min_length=1,
    )

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

    report_text: str

    reporter_id: str | None = None

    analysis: CommunityReportAnalysis

    analysis_source: AnalysisSource = Field(
        ...,
        description=(
            "Mechanism that produced the analysis. "
            "Does not verify the report."
        ),
    )

    verified: bool = Field(
        default=False,
        description=(
            "Whether the report was independently verified."
        ),
    )

    resolved: bool = Field(
        default=False,
        description=(
            "Whether the report has been operationally resolved "
            "or closed by the operations team."
        ),
    )

    verified_at: datetime | None = None

    resolved_at: datetime | None = None

    created_at: datetime
