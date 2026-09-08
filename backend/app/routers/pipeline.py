from datetime import datetime, timezone

from fastapi import APIRouter, Query

from app.schemas.risk import (
    FloodRiskInput,
    EarthquakeRiskInput,
    RiskAssessment,
)

from app.schemas.decision import (
    DecisionInput,
    FinalDecision,
)

from app.schemas.pipeline import (
    MonjedAssessment,
)

from app.schemas.accessibility import (
    AccessibilityNeed,
    AccessibilityProfile,
)

from app.schemas.assistance import (
    AssistanceRequestRecord,
)

from app.services.flood_risk import (
    calculate_flood_risk,
)

from app.services.earthquake_risk import (
    calculate_earthquake_risk,
)

from app.services.community_report_store import (
    get_recent_reports,
)

from app.services.community_evidence_mapper import (
    reports_to_evidence,
)

from app.services.accessibility_adapter import (
    adapt_decision_for_accessibility,
)

from app.services.assistance_store import (
    create_decision_assistance_request,
)

from app.engines.decision import (
    evaluate_decision,
)

from app.services.ai_adapter import (
    build_ai_payload,
)

from AI.ai_alert.gemini_alert import (
    generate_alert,
)

from app.services.persistence_service import (
    safe_persist_assessment,
)

from app.services.persistence_service import (
    safe_persist_assessment,
)

from app.services.alert_normalizer import (
    normalize_alert,
)

from app.services.alert_dispatcher import (
    dispatch_alert,
)

from app.services.sms.recipients import (
    get_sms_recipients_for_zone,
)

from database.alerts_repository import (
    create_alert,
)

router = APIRouter(
    prefix="/pipeline",
    tags=["MONJED Pipeline"],
)


# ============================================================
# DECISION BUILDER
# ============================================================

def build_final_decision(
    risk: RiskAssessment,
) -> FinalDecision:
    """
    Combine scientific risk assessment with recent community
    evidence to produce the operational decision.

    Community evidence may modify operational actions,
    but it does NOT modify the scientific risk score.
    """

    reports = get_recent_reports(
        zone_id=risk.zone_id,
        max_age_minutes=180,
    )

    evidence = reports_to_evidence(
        reports
    )

    decision_input = DecisionInput(
        hazard=risk.hazard,
        zone_id=risk.zone_id,
        risk_score=risk.risk_score,
        risk_level=risk.risk_level,
        confidence=risk.confidence,
        evidence=evidence,
    )

    decision_result = evaluate_decision(
        decision_input
    )

    return FinalDecision(
        **decision_result
    )


# ============================================================
# ACCESSIBILITY LAYER
# ============================================================

def build_accessible_action(
    decision: FinalDecision,
    accessibility_needs: list[AccessibilityNeed] | None,
):
    """
    Adapt backend-approved actions for accessibility needs.

    Accessibility does NOT modify scientific risk.
    """

    if not accessibility_needs:
        return None

    profile = AccessibilityProfile(
        accessibility_needs=accessibility_needs
    )

    return adapt_decision_for_accessibility(
        decision=decision,
        profile=profile,
    )


# ============================================================
# HUMAN ASSISTANCE ESCALATION
# ============================================================

def build_assistance_request(
    decision: FinalDecision,
    accessibility_needs: list[AccessibilityNeed] | None,
) -> AssistanceRequestRecord | None:
    """
    Automatically create an assistance request when the
    deterministic Decision Engine requires human review.

    Current safety policy:

    people_trapped
        -> human_review_required
        -> critical rescue_support request
        -> trained responder required

    IMPORTANT:
    - This does NOT automatically assign a responder.
    - Matching remains controlled by the safety-aware
      volunteer matching layer.
    - Community reports remain unverified unless separately
      confirmed.
    """

    # --------------------------------------------------------
    # 1. ESCALATE ONLY HUMAN-REVIEW DECISIONS
    # --------------------------------------------------------

    if (
        decision.decision_status
        != "human_review_required"
    ):
        return None

    # --------------------------------------------------------
    # 2. LOAD RECENT COMMUNITY REPORTS
    # --------------------------------------------------------

    reports = get_recent_reports(
        zone_id=decision.zone_id,
        max_age_minutes=180,
    )

    # --------------------------------------------------------
    # 3. IDENTIFY REPORTS SUPPORTING THE ESCALATION
    #
    # Currently people_trapped is the safety-critical signal
    # that triggers human_review_required.
    # --------------------------------------------------------

    escalation_reports = [
        report
        for report in reports
        if report.analysis.people_trapped
    ]

    # Human review should currently have a corresponding
    # trapped-person report.
    #
    # If none exists, fail safely instead of inventing
    # location/report metadata.
    if not escalation_reports:

        print(
            "MONJED assistance escalation warning: "
            "human_review_required was produced, but no recent "
            "people_trapped report was found."
        )

        return None

    # --------------------------------------------------------
    # 4. USE MOST RECENT RELEVANT LOCATION
    # --------------------------------------------------------

    latest_report = max(
        escalation_reports,
        key=lambda report: report.created_at,
    )

    location = latest_report.location

    # --------------------------------------------------------
    # 5. TRACE SOURCE REPORTS
    # --------------------------------------------------------

    source_report_ids = [
        report.report_id
        for report in escalation_reports
    ]

    # Remove duplicates while preserving order.
    source_report_ids = list(
        dict.fromkeys(
            source_report_ids
        )
    )

    # --------------------------------------------------------
    # 6. ACCESSIBILITY METADATA
    # --------------------------------------------------------

    normalized_accessibility_needs = list(
        dict.fromkeys(
            accessibility_needs or []
        )
    )

    # --------------------------------------------------------
    # 7. CREATE SAFE SYSTEM-GENERATED REQUEST
    # --------------------------------------------------------

    return create_decision_assistance_request(
        zone_id=decision.zone_id,
        location=location,
        hazard=decision.hazard,
        request_type="rescue_support",
        priority="critical",
        description=(
            "Human review is required because recent community "
            "evidence indicates that people may be trapped. "
            "Trained rescue assistance is required. "
            "Community evidence remains unverified unless "
            "separately confirmed."
        ),
        evidence_used=decision.evidence_used,
        source_report_ids=source_report_ids,
        accessibility_needs=(
            normalized_accessibility_needs
        ),
        requires_trained_responder=True,
    )


# ============================================================
# AI COMMUNICATION LAYER
# ============================================================

def add_ai_alert(
    assessment: MonjedAssessment,
    accessibility_action=None,
) -> MonjedAssessment:
    """
    Complete MONJED communication + delivery pipeline.

    Flow:

    deterministic backend assessment
        ->
    AI communication / deterministic fallback
        ->
    protected alert normalization
        ->
    core persistence
        ->
    recipient selection
        ->
    dashboard / SMS / voice dispatch
        ->
    final alert + delivery persistence

    IMPORTANT:
    - Generative AI cannot modify scientific risk.
    - Generative AI cannot modify the deterministic decision.
    - MongoDB cannot modify risk or decision.
    - SMS / Voice are gated by notification_required.
    """

    # ========================================================
    # 1. BUILD BACKEND-OWNED AI PAYLOAD
    # ========================================================

    backend_payload = build_ai_payload(
        assessment=assessment,
        accessibility=accessibility_action,
    )

    # ========================================================
    # 2. AI COMMUNICATION / DETERMINISTIC FALLBACK
    # ========================================================

    raw_ai_alert = generate_alert(
        backend_payload
    )

    # ========================================================
    # 3. PROTECTED NORMALIZATION
    #
    # Backend values remain authoritative.
    # ========================================================

    normalized_alert = normalize_alert(
        ai_alert=raw_ai_alert,
        backend_payload=backend_payload,
    )

    # ========================================================
    # 4. FINAL API ASSESSMENT
    # ========================================================

    final_assessment = MonjedAssessment(
        risk=assessment.risk,
        decision=assessment.decision,
        accessible_action=(
            assessment.accessible_action
        ),
        assistance_request=(
            assessment.assistance_request
        ),
        ai_alert=normalized_alert,
    )

    # ========================================================
    # 5. PERSIST SCIENTIFIC RISK + DECISION
    # ========================================================

    persistence_result = (
        safe_persist_assessment(
            final_assessment
        )
    )

    # ========================================================
    # 6. RECIPIENT SELECTION
    # ========================================================

    sms_recipients = []

    if normalized_alert.get(
        "notification_required",
        False,
    ):

        sms_recipients = get_sms_recipients_for_zone(
            assessment.risk.zone_id
        )

    # ========================================================
    # 7. DELIVERY
    #
    # Dispatcher itself respects notification_required.
    # Dashboard always receives the update.
    # ========================================================

    try:

        delivery_result = dispatch_alert(
            alert=normalized_alert,
            sms_recipients=sms_recipients,
        )

    except Exception as exc:

        print(
            "MONJED delivery warning: "
            f"{type(exc).__name__}: {exc}"
        )

        delivery_result = {
            "dashboard":
                None,

            "sms":
                [],

            "voice":
                {
                    "success":
                        False,

                    "error":
                        type(exc).__name__,
                },

            "notification_required":
                bool(
                    normalized_alert.get(
                        "notification_required",
                        False,
                    )
                ),
        }

    # ========================================================
    # 8. STORE FINAL NORMALIZED ALERT + DELIVERY RESULT
    # ========================================================

    alert_for_storage = dict(
        normalized_alert
    )

    if persistence_result.get(
        "success"
    ):

        alert_for_storage[
            "risk_id"
        ] = persistence_result.get(
            "risk_id"
        )

        alert_for_storage[
            "decision_id"
        ] = persistence_result.get(
            "decision_id"
        )

    try:

        create_alert(
            alert_data=alert_for_storage,
            delivery_result=delivery_result,
        )

    except Exception as exc:

        # Delivery already happened.
        # Database failure must not invalidate the assessment.
        print(
            "MONJED alert persistence warning: "
            f"{type(exc).__name__}: {exc}"
        )

    # ========================================================
    # 9. RETURN ASSESSMENT
    # ========================================================

    return final_assessment.model_copy(
        update={
            "delivery": delivery_result,
        }
    )
    
# ============================================================
# FLOOD PIPELINE
# ============================================================

@router.post(
    "/flood",
    response_model=MonjedAssessment,
)
def flood_pipeline(
    data: FloodRiskInput,
    accessibility_needs: list[AccessibilityNeed] | None = Query(
        default=None
    ),
):

    # --------------------------------------------------------
    # 1. SCIENTIFIC RISK ENGINE
    # --------------------------------------------------------

    risk_score, risk_level, reasons, confidence = (
        calculate_flood_risk(
            data
        )
    )

    risk_assessment = RiskAssessment(
        hazard="flood",
        zone_id=data.zone_id,
        risk_score=risk_score,
        risk_level=risk_level,
        confidence=confidence,
        reasons=reasons,
        evaluated_at=datetime.now(
            timezone.utc
        ),
    )

    # --------------------------------------------------------
    # 2. OPERATIONAL DECISION ENGINE
    # --------------------------------------------------------

    decision = build_final_decision(
        risk_assessment
    )

    # --------------------------------------------------------
    # 3. ACCESSIBILITY LAYER
    # --------------------------------------------------------

    accessible_action = build_accessible_action(
        decision,
        accessibility_needs,
    )

    # --------------------------------------------------------
    # 4. HUMAN ASSISTANCE ESCALATION
    # --------------------------------------------------------

    assistance_request = (
        build_assistance_request(
            decision=decision,
            accessibility_needs=(
                accessibility_needs
            ),
        )
    )

    # --------------------------------------------------------
    # 5. MONJED ASSESSMENT
    # --------------------------------------------------------

    assessment = MonjedAssessment(
        risk=risk_assessment,
        decision=decision,
        accessible_action=accessible_action,
        assistance_request=assistance_request,
    )

    # --------------------------------------------------------
    # 6. AI COMMUNICATION LAYER
    # --------------------------------------------------------

    return add_ai_alert(
        assessment,
        accessible_action,
    )


# ============================================================
# EARTHQUAKE PIPELINE
# ============================================================

@router.post(
    "/earthquake",
    response_model=MonjedAssessment,
)
def earthquake_pipeline(
    data: EarthquakeRiskInput,
    accessibility_needs: list[AccessibilityNeed] | None = Query(
        default=None
    ),
):

    # --------------------------------------------------------
    # 1. SCIENTIFIC RISK / IMPACT ENGINE
    # --------------------------------------------------------

    risk_score, risk_level, reasons, confidence = (
        calculate_earthquake_risk(
            data
        )
    )

    risk_assessment = RiskAssessment(
        hazard="earthquake",
        zone_id=data.zone_id,
        risk_score=risk_score,
        risk_level=risk_level,
        confidence=confidence,
        reasons=reasons,
        evaluated_at=datetime.now(
            timezone.utc
        ),
    )

    # --------------------------------------------------------
    # 2. OPERATIONAL DECISION ENGINE
    # --------------------------------------------------------

    decision = build_final_decision(
        risk_assessment
    )

    # --------------------------------------------------------
    # 3. ACCESSIBILITY LAYER
    # --------------------------------------------------------

    accessible_action = build_accessible_action(
        decision,
        accessibility_needs,
    )

    # --------------------------------------------------------
    # 4. HUMAN ASSISTANCE ESCALATION
    # --------------------------------------------------------

    assistance_request = (
        build_assistance_request(
            decision=decision,
            accessibility_needs=(
                accessibility_needs
            ),
        )
    )

    # --------------------------------------------------------
    # 5. MONJED ASSESSMENT
    # --------------------------------------------------------

    assessment = MonjedAssessment(
        risk=risk_assessment,
        decision=decision,
        accessible_action=accessible_action,
        assistance_request=assistance_request,
    )

    # --------------------------------------------------------
    # 6. AI COMMUNICATION LAYER
    # --------------------------------------------------------

    return add_ai_alert(
        assessment,
        accessible_action,
    )