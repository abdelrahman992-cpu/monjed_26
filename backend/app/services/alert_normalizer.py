"""
MONJED AI - Alert Normalizer

Converts AI communication output + authoritative backend data
into one normalized MONJED alert for delivery channels.

Architecture:

Backend Risk + Decision  ──────┐
                               ↓
AI Communication Output → Alert Normalizer
                               ↓
                    Dashboard / SMS / Voice


SOURCE-OF-TRUTH RULES:

Backend owns:
- hazard type
- risk score
- risk level
- confidence when available
- decision status
- notification_required
- current action
- backup action
- accessibility instructions

AI may provide:
- title
- hazard message / explanation
- community evidence summary
- alert message
- communication wording

IMPORTANT:
- Does NOT calculate risk.
- Does NOT make decisions.
- Does NOT modify backend-approved actions.
- Does NOT allow AI output to override protected backend fields.
"""


from copy import deepcopy
from datetime import datetime, timezone


# ============================================================
# HELPERS
# ============================================================


def _safe_list(value) -> list:
    """
    Safely return a list.
    """

    return value if isinstance(value, list) else []



def _safe_dict(value) -> dict:
    """
    Safely return a dictionary.
    """

    return value if isinstance(value, dict) else {}



def _clean_text(value, default="") -> str:
    """
    Normalize unnecessary whitespace without
    changing the meaning of the text.
    """

    if value is None:
        return default

    text = " ".join(
        str(value).split()
    )

    return text if text else default



def _get_value(
    data: dict,
    primary: str,
    fallback: str,
    default=None,
):
    """
    Read a value using a primary key
    and then a compatible fallback key.
    """

    value = data.get(
        primary
    )

    if value is not None:
        return value

    return data.get(
        fallback,
        default,
    )



def _get_backend_decision(
    backend_payload: dict,
) -> dict:
    """
    Backend decision is always authoritative.
    """

    return _safe_dict(
        backend_payload.get(
            "decision",
            {},
        )
    )



def _first_reason(
    hazard: dict,
) -> str:
    """
    Return first backend reason if available.
    """

    reasons = _safe_list(
        hazard.get(
            "reasons",
            [],
        )
    )

    for reason in reasons:

        clean_reason = _clean_text(
            reason
        )

        if clean_reason:
            return clean_reason

    return ""



def _hazard_type(
    hazard: dict,
) -> str:
    """
    Support both backend and AI hazard field names.
    """

    return _clean_text(
        _get_value(
            hazard,
            "hazard",
            "type",
            "unknown",
        ),
        "unknown",
    ).lower()



def _find_ai_hazard(
    ai_hazards: list,
    hazard_type: str,
) -> dict:
    """
    Find corresponding AI communication object
    for the same hazard type.

    AI fields are used only for communication,
    never for authoritative risk values.
    """

    for hazard in ai_hazards:

        if not isinstance(
            hazard,
            dict,
        ):
            continue

        current_type = _clean_text(
            _get_value(
                hazard,
                "type",
                "hazard",
                "",
            )
        ).lower()

        if current_type == hazard_type:
            return hazard

    return {}


# ============================================================
# COMMUNITY SUMMARY
# ============================================================


def _build_community_summary(
    ai_alert: dict,
    backend_payload: dict,
) -> str:
    """
    Preserve AI/fallback community evidence summary.

    If unavailable, generate a deterministic
    informational fallback from backend metadata.
    """

    summary = _clean_text(
        ai_alert.get(
            "community_evidence_summary"
        )
    )

    if summary:
        return summary


    summary = _clean_text(
        ai_alert.get(
            "summary"
        )
    )

    if summary:
        return summary


    community_evidence = _safe_dict(
        backend_payload.get(
            "community_evidence",
            {},
        )
    )


    evidence_count = community_evidence.get(
        "matching_reports",
        0,
    )


    try:
        evidence_count = int(
            evidence_count
        )

    except (
        TypeError,
        ValueError,
    ):
        evidence_count = 0


    if evidence_count <= 0:

        return (
            "No recent community evidence items "
            "were used in the operational decision."
        )


    if evidence_count == 1:

        return (
            "1 community evidence item was considered "
            "in the operational decision."
        )


    return (
        f"{evidence_count} community evidence items "
        f"were considered in the operational decision."
    )


# ============================================================
# ALERT MESSAGE FALLBACK
# ============================================================


def _build_alert_message(
    ai_alert: dict,
    backend_payload: dict,
    backend_decision: dict,
) -> str:
    """
    Preserve communication output if available.

    If AI communication is unavailable,
    create a small deterministic delivery fallback
    using backend-approved information only.
    """

    message = _clean_text(
        ai_alert.get(
            "alert_message"
        )
    )

    if message:
        return message


    message = _clean_text(
        ai_alert.get(
            "summary"
        )
    )

    if message:
        return message


    country = _clean_text(
        backend_payload.get(
            "country"
        )
    )


    zone_id = _clean_text(
        backend_payload.get(
            "zone_id"
        )
    )


    current_action = _clean_text(
        backend_decision.get(
            "current_action"
        )
    )


    location_parts = []

    if zone_id:
        location_parts.append(
            zone_id
        )

    if country:
        location_parts.append(
            country
        )


    location = ", ".join(
        location_parts
    )


    parts = []


    if location:

        parts.append(
            f"MONJED alert for {location}."
        )

    else:

        parts.append(
            "MONJED alert."
        )


    if current_action:

        parts.append(
            f"Action: {current_action}"
        )


    return " ".join(
        parts
    )


# ============================================================
# HAZARD NORMALIZATION
# ============================================================


def _normalize_hazards(
    ai_alert: dict,
    backend_payload: dict,
) -> list:
    """
    Normalize hazards while keeping backend risk
    values as the authoritative source.

    AI may contribute only communication wording.
    """

    normalized = []


    backend_hazards = _safe_list(
        backend_payload.get(
            "hazards",
            [],
        )
    )


    ai_hazards = _safe_list(
        ai_alert.get(
            "hazards",
            [],
        )
    )


    # --------------------------------------------------------
    # Preferred path:
    # backend hazards are authoritative
    # --------------------------------------------------------

    if backend_hazards:

        for backend_hazard in backend_hazards:

            if not isinstance(
                backend_hazard,
                dict,
            ):
                continue


            hazard_type = _hazard_type(
                backend_hazard
            )


            ai_hazard = _find_ai_hazard(
                ai_hazards,
                hazard_type,
            )


            # ------------------------------------------------
            # Communication message
            # ------------------------------------------------

            message = _clean_text(
                ai_hazard.get(
                    "message"
                )
            )


            if not message:

                message = _first_reason(
                    backend_hazard
                )


            if not message:

                message = (
                    "Risk detected. "
                    "Follow official safety guidance."
                )


            # ------------------------------------------------
            # Confidence
            # ------------------------------------------------
            #
            # Confidence is protected scientific metadata.
            # Prefer backend confidence only.
            # ------------------------------------------------

            confidence = backend_hazard.get(
                "confidence"
            )


            normalized.append(
                {
                    "type":
                        hazard_type,

                    "risk_level":
                        _get_value(
                            backend_hazard,
                            "risk_level",
                            "level",
                            "unknown",
                        ),

                    "risk_score":
                        _get_value(
                            backend_hazard,
                            "risk_score",
                            "score",
                            0,
                        ),

                    "confidence":
                        confidence,

                    "message":
                        message,
                }
            )


        return normalized


    # --------------------------------------------------------
    # Defensive fallback
    # --------------------------------------------------------
    #
    # Normally backend hazards should always exist.
    # This path prevents crashes in incomplete tests or
    # legacy payloads.
    # --------------------------------------------------------

    for ai_hazard in ai_hazards:

        if not isinstance(
            ai_hazard,
            dict,
        ):
            continue


        message = _clean_text(
            ai_hazard.get(
                "message"
            ),
            "Risk detected. Follow official safety guidance.",
        )


        normalized.append(
            {
                "type":
                    _get_value(
                        ai_hazard,
                        "type",
                        "hazard",
                        "unknown",
                    ),

                "risk_level":
                    _get_value(
                        ai_hazard,
                        "risk_level",
                        "level",
                        "unknown",
                    ),

                "risk_score":
                    _get_value(
                        ai_hazard,
                        "risk_score",
                        "score",
                        0,
                    ),

                "confidence":
                    ai_hazard.get(
                        "confidence"
                    ),

                "message":
                    message,
            }
        )


    return normalized


# ============================================================
# MAIN NORMALIZER
# ============================================================


def normalize_alert(
    ai_alert: dict,
    backend_payload: dict,
) -> dict:
    """
    Convert MONJED backend + AI communication output
    into the normalized alert used by delivery channels.

    Backend remains the source of truth for:
    - scientific risk
    - operational decision
    - notification gating
    """

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    if not isinstance(
        ai_alert,
        dict,
    ):

        raise TypeError(
            "ai_alert must be a dictionary."
        )


    if not isinstance(
        backend_payload,
        dict,
    ):

        raise TypeError(
            "backend_payload must be a dictionary."
        )


    # --------------------------------------------------------
    # Backend authoritative decision
    # --------------------------------------------------------

    backend_decision = _get_backend_decision(
        backend_payload
    )


    notification_required = bool(
        backend_decision.get(
            "notification_required",
            False,
        )
    )


    # --------------------------------------------------------
    # Communication fields
    # --------------------------------------------------------

    community_summary = (
        _build_community_summary(
            ai_alert,
            backend_payload,
        )
    )


    alert_message = (
        _build_alert_message(
            ai_alert,
            backend_payload,
            backend_decision,
        )
    )


    # --------------------------------------------------------
    # Timestamp
    # --------------------------------------------------------

    generated_at = datetime.now(
        timezone.utc
    ).isoformat()


    # --------------------------------------------------------
    # Normalized output
    # --------------------------------------------------------

    return {

        "title":
            _clean_text(
                ai_alert.get(
                    "title"
                ),
                "MONJED Alert",
            ),


        "zone_id":
            _clean_text(
                backend_payload.get(
                    "zone_id"
                ),
                "UNKNOWN",
            ),


        "country":
            _clean_text(
                backend_payload.get(
                    "country"
                ),
                _clean_text(
                    ai_alert.get(
                        "country"
                    ),
                    "UNKNOWN",
                ),
            ),


        "language":
            _clean_text(
                backend_payload.get(
                    "language"
                ),
                "en",
            ).lower(),


        "generated_at":
            generated_at,


        # ====================================================
        # SCIENTIFIC RISK
        # ====================================================

        "hazards":
            _normalize_hazards(
                ai_alert,
                backend_payload,
            ),


        # ====================================================
        # COMMUNITY COMMUNICATION
        # ====================================================

        "community_evidence_summary":
            community_summary,


        # ====================================================
        # BACKEND DECISION — SOURCE OF TRUTH
        # ====================================================

        "final_decision": {

            "decision_status":
                backend_decision.get(
                    "decision_status"
                ),

            "notification_required":
                notification_required,

            "current_action":
                backend_decision.get(
                    "current_action"
                ),

            "backup_action":
                backend_decision.get(
                    "backup_action"
                ),

            "accessibility_instructions":
                deepcopy(
                    _safe_list(
                        backend_decision.get(
                            "accessibility_instructions",
                            [],
                        )
                    )
                ),
        },


        # ====================================================
        # DELIVERY GATE
        # ====================================================

        "notification_required":
            notification_required,


        # ====================================================
        # ACCESSIBILITY
        # ====================================================

        "accessibility_needs":
            deepcopy(
                _safe_list(
                    backend_payload.get(
                        "accessibility_needs",
                        [],
                    )
                )
            ),


        # ====================================================
        # COMMUNICATION
        # ====================================================

        "alert_message":
            alert_message,


        "alert_source":
            _clean_text(
                ai_alert.get(
                    "alert_source"
                ),
                "DETERMINISTIC_FALLBACK",
            ),
    }