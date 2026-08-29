from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.schemas.community_report import (
    AnalysisSource,
    CommunityReportInput,
    CommunityReportAnalysis,
    CommunityReportRecord,
)


_reports: list[CommunityReportRecord] = []



# ============================================================
# SAVE REPORT
# ============================================================

def save_report(
    report: CommunityReportInput,
    analysis: CommunityReportAnalysis,
    analysis_source: AnalysisSource,
) -> CommunityReportRecord:


    now = datetime.now(
        timezone.utc
    )


    duplicate_window = (
        now - timedelta(minutes=5)
    )


    zone_id = report.zone_id.strip()

    location = report.location.strip().lower()

    text = report.report_text.strip().lower()



    for existing in _reports:


        if (

            existing.zone_id.strip()
            == zone_id

            and

            existing.location.strip().lower()
            == location

            and

            existing.report_text.strip().lower()
            == text

            and

            existing.latitude
            == report.latitude

            and

            existing.longitude
            == report.longitude

            and

            existing.created_at
            >= duplicate_window

        ):

            return existing



    record = CommunityReportRecord(

    report_id=str(
        uuid4()
    ),

    zone_id=zone_id,

    location=report.location.strip(),

    latitude=report.latitude,

    longitude=report.longitude,

    report_text=report.report_text.strip(),

    reporter_id=report.reporter_id,

    analysis=analysis,

    analysis_source=analysis_source,

    verified=False,

    resolved=False,

    verified_at=None,

    resolved_at=None,

    created_at=now,
)

    _reports.append(
        record
    )


    return record



# ============================================================
# RECENT REPORTS
# ============================================================

def get_recent_reports(
    zone_id: str,
    max_age_minutes: int = 180,
):


    cutoff = (
        datetime.now(timezone.utc)
        -
        timedelta(minutes=max_age_minutes)
    )


    zone_id = zone_id.strip()


    return [

        report

        for report in _reports

        if (

            report.zone_id.strip()
            == zone_id

            and

            report.created_at >= cutoff

            and

            not report.resolved

        )

    ]

# ============================================================
# GET ALL REPORTS
# ============================================================

def get_all_reports():
    """
    Return all stored community reports.

    Primarily used by the operations/admin frontend.
    """

    return list(
        _reports
    )


# ============================================================
# GET REPORT
# ============================================================

def get_report(
    report_id: str,
) -> CommunityReportRecord | None:

    report_id = report_id.strip()

    if not report_id:
        return None

    for report in _reports:

        if report.report_id == report_id:
            return report

    return None


# ============================================================
# VERIFY REPORT
# ============================================================

def verify_report(
    report_id: str,
) -> CommunityReportRecord | None:
    """
    Mark a report as independently verified.

    Verification affects report trust/workflow status only.
    It does not modify scientific risk.
    """

    report = get_report(
        report_id
    )

    if report is None:
        return None

    if not report.verified:

        report.verified = True

        report.verified_at = datetime.now(
            timezone.utc
        )

    return report


# ============================================================
# RESOLVE REPORT
# ============================================================

def resolve_report(
    report_id: str,
) -> CommunityReportRecord | None:
    """
    Close a community report operationally.

    This does not modify historical scientific risk data.
    """

    report = get_report(
        report_id
    )

    if report is None:
        return None

    if not report.resolved:

        report.resolved = True

        report.resolved_at = datetime.now(
            timezone.utc
        )

    return report

# ============================================================
# CLEAR
# ============================================================

def clear_reports():

    _reports.clear()