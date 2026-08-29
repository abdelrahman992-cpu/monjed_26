from datetime import datetime, timezone

from app.schemas.community_report import (
    CommunityReportRecord,
)

from app.schemas.decision import (
    CommunityEvidence,
)


# ============================================================
# HELPERS
# ============================================================

def _calculate_age_minutes(
    created_at: datetime,
    now: datetime,
) -> int:
    """
    Calculate report age safely in minutes.

    Old/in-memory records may occasionally contain a naive
    datetime, so treat them as UTC for consistency.
    """

    if created_at.tzinfo is None:
        created_at = created_at.replace(
            tzinfo=timezone.utc
        )
    else:
        created_at = created_at.astimezone(
            timezone.utc
        )

    age_seconds = (
        now - created_at
    ).total_seconds()

    return max(
        0,
        int(age_seconds // 60),
    )


def _build_description(
    report: CommunityReportRecord,
) -> str:
    """
    Build a concise evidence description.

    Prefer analyzer-extracted factual evidence when available.
    Fall back to the original report text.

    CommunityEvidence allows a maximum of 500 characters.
    """

    extracted = [
        str(item).strip()
        for item in report.analysis.extracted_evidence
        if str(item).strip()
    ]

    if extracted:
        description = "; ".join(
            extracted
        )
    else:
        description = (
            report.report_text.strip()
        )

    if len(description) < 3:
        description = (
            report.report_text.strip()
        )

    return description[:500]


def _append_evidence(
    evidence: list[CommunityEvidence],
    report: CommunityReportRecord,
    evidence_type: str,
    age_minutes: int,
    description: str,
) -> None:
    """
    Append one normalized operational evidence item.
    """

    evidence.append(
        CommunityEvidence(
            zone_id=report.zone_id,
            evidence_type=evidence_type,
            description=description,
            age_minutes=age_minutes,
            verified=report.verified,
        )
    )


# ============================================================
# REPORTS -> OPERATIONAL EVIDENCE
# ============================================================

def reports_to_evidence(
    reports: list[CommunityReportRecord],
) -> list[CommunityEvidence]:
    """
    Convert analyzed community reports into operational
    evidence understood by MONJED's Decision Engine.

    IMPORTANT:
    - Community evidence does NOT modify scientific risk.
    - A report may produce multiple evidence items.
    - AI analysis does NOT make the report verified.
    - help_needed alone does NOT imply people_trapped.
    """

    evidence: list[CommunityEvidence] = []

    now = datetime.now(
        timezone.utc
    )

    for report in reports:

        age_minutes = _calculate_age_minutes(
            created_at=report.created_at,
            now=now,
        )

        analysis = report.analysis

        description = _build_description(
            report
        )

        specific_evidence_added = False

        # ====================================================
        # 1. PEOPLE TRAPPED
        #
        # Highest operational importance.
        # Decision Engine will trigger human review.
        # ====================================================

        if analysis.people_trapped:

            _append_evidence(
                evidence=evidence,
                report=report,
                evidence_type="people_trapped",
                age_minutes=age_minutes,
                description=description,
            )

            specific_evidence_added = True


        # ====================================================
        # 2. BUILDING DAMAGE
        # ====================================================

        if analysis.building_damage:

            _append_evidence(
                evidence=evidence,
                report=report,
                evidence_type="building_damage",
                age_minutes=age_minutes,
                description=description,
            )

            specific_evidence_added = True


        # ====================================================
        # 3. INFRASTRUCTURE DAMAGE
        # ====================================================

        if analysis.infrastructure_damage:

            _append_evidence(
                evidence=evidence,
                report=report,
                evidence_type="infrastructure_damage",
                age_minutes=age_minutes,
                description=description,
            )

            specific_evidence_added = True


        # ====================================================
        # 4. BLOCKED / UNSAFE ROAD
        # ====================================================

        if analysis.blocked_road:

            _append_evidence(
                evidence=evidence,
                report=report,
                evidence_type="blocked_road",
                age_minutes=age_minutes,
                description=description,
            )

            specific_evidence_added = True


        # ====================================================
        # 5. RISING WATER
        # ====================================================

        if analysis.rising_water:

            _append_evidence(
                evidence=evidence,
                report=report,
                evidence_type="rising_water",
                age_minutes=age_minutes,
                description=description,
            )

            specific_evidence_added = True


        # ====================================================
        # 6. OTHER COMMUNITY EVIDENCE
        #
        # The report was considered, but it did not contain
        # one of the operational signals currently handled
        # explicitly by the Decision Engine.
        #
        # We deliberately DO NOT convert:
        # - help_needed
        # - transportation_needed
        # - mobility_assistance_needed
        #
        # into people_trapped or structural evidence.
        # Those concepts remain separate.
        # ====================================================

        if not specific_evidence_added:

            _append_evidence(
                evidence=evidence,
                report=report,
                evidence_type="other",
                age_minutes=age_minutes,
                description=description,
            )

    return evidence