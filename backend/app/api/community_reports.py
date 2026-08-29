from fastapi import (
    APIRouter,
    HTTPException,
)

from app.schemas.community_report import (
    CommunityReportInput,
    CommunityReportAnalysis,
    CommunityReportRecord,
)

from app.services.community_report_analyzer import (
    analyze_community_report,
)

from app.services.community_report_store import (
    get_all_reports,
    get_recent_reports,
    resolve_report,
    save_report,
    verify_report,
)


router = APIRouter(
    prefix="/api/community-reports",
    tags=["Community Reports"],
)


# ============================================================
# ANALYZE REPORT
# ============================================================

@router.post(
    "/analyze",
    response_model=CommunityReportAnalysis,
)
def analyze_report(
    report: CommunityReportInput,
) -> CommunityReportAnalysis:
    """
    Analyze a community report without storing it.

    The public response contains only the structured analysis.

    analysis_source is intentionally not returned here because
    this endpoint's response contract is CommunityReportAnalysis.
    """

    analysis, _analysis_source = (
        analyze_community_report(
            report
        )
    )

    return analysis


# ============================================================
# SUBMIT AND STORE REPORT
# ============================================================

@router.post(
    "/submit",
    response_model=CommunityReportRecord,
)
def submit_report(
    report: CommunityReportInput,
) -> CommunityReportRecord:
    """
    Analyze and store a community report.

    The backend records both:
    - the structured analysis
    - the mechanism that produced that analysis

    analysis_source does NOT indicate that the report
    has been verified.
    """

    analysis, analysis_source = (
        analyze_community_report(
            report
        )
    )

    return save_report(
        report=report,
        analysis=analysis,
        analysis_source=analysis_source,
    )

# ============================================================
# LIST REPORTS
# ============================================================

@router.get(
    "",
    response_model=list[CommunityReportRecord],
)
def list_reports(
    zone_id: str | None = None,
    verified: bool | None = None,
    resolved: bool | None = None,
) -> list[CommunityReportRecord]:
    """
    Return community reports for the operations frontend.

    Optional filters:
    - zone_id
    - verified
    - resolved
    """

    reports = get_all_reports()

    if zone_id is not None:

        normalized_zone = zone_id.strip()

        reports = [
            report
            for report in reports
            if report.zone_id.strip() == normalized_zone
        ]

    if verified is not None:

        reports = [
            report
            for report in reports
            if report.verified == verified
        ]

    if resolved is not None:

        reports = [
            report
            for report in reports
            if report.resolved == resolved
        ]

    return reports


# ============================================================
# VERIFY REPORT
# ============================================================

@router.patch(
    "/{report_id}/verify",
    response_model=CommunityReportRecord,
)
def verify_community_report(
    report_id: str,
) -> CommunityReportRecord:

    report = verify_report(
        report_id
    )

    if report is None:

        raise HTTPException(
            status_code=404,
            detail="Community report not found.",
        )

    return report


# ============================================================
# RESOLVE REPORT
# ============================================================

@router.patch(
    "/{report_id}/resolve",
    response_model=CommunityReportRecord,
)
def resolve_community_report(
    report_id: str,
) -> CommunityReportRecord:

    report = resolve_report(
        report_id
    )

    if report is None:

        raise HTTPException(
            status_code=404,
            detail="Community report not found.",
        )

    return report

# ============================================================
# RECENT REPORTS
# ============================================================

@router.get(
    "/recent/{zone_id}",
    response_model=list[CommunityReportRecord],
)
def recent_reports(
    zone_id: str,
) -> list[CommunityReportRecord]:
    """
    Return recently stored community reports for a zone.
    """

    return get_recent_reports(
        zone_id=zone_id,
    )