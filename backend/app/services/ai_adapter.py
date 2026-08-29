"""
MONJED AI - AI Adapter

Converts deterministic MONJED backend assessment
into a safe AI communication payload.

Architecture:

Risk Engine
      ↓
Decision Engine
      ↓
Accessibility Layer
      ↓
AI Adapter
      ↓
Gemini Alert Layer


IMPORTANT:
- AI does NOT calculate risk.
- AI does NOT make decisions.
- AI does NOT modify scientific risk.
- AI receives backend-approved actions only.
- Backend remains the source of truth.
"""


from copy import deepcopy


# ============================================================
# CONSTANTS
# ============================================================


SUPPORTED_LANGUAGES = {
    "en",
    "ar",
    "fr",
    "sw",
}


VALID_RISK_LEVELS = {
    "unknown",
    "low",
    "moderate",
    "high",
    "critical",
}


VALID_ACCESSIBILITY_NEEDS = {
    "mobility",
    "visual",
    "hearing",
    "cognitive",
}


DEFAULT_COUNTRY = "Egypt"


# ============================================================
# VALIDATION HELPERS
# ============================================================


def _validate_language(language) -> str:
    """
    Normalize requested communication language.

    Unsupported languages safely fall back to English.
    """

    normalized = (
        str(language)
        .lower()
        .strip()
    )

    return (
        normalized
        if normalized in SUPPORTED_LANGUAGES
        else "en"
    )


def _validate_accessibility_needs(
    accessibility_needs,
) -> list:
    """
    Validate supported accessibility needs.
    """

    if not accessibility_needs:
        return []


    if not isinstance(
        accessibility_needs,
        list,
    ):
        raise TypeError(
            "accessibility_needs must be a list."
        )


    normalized = []


    for need in accessibility_needs:

        value = (
            str(need)
            .lower()
            .strip()
        )


        if value not in VALID_ACCESSIBILITY_NEEDS:
            raise ValueError(
                f"Unsupported accessibility need: {need}"
            )


        if value not in normalized:
            normalized.append(
                value
            )


    return normalized


def _validate_risk(
    risk,
) -> str:
    """
    Validate backend scientific risk fields.

    Does not calculate or reinterpret risk.
    """

    risk_level = (
        str(
            getattr(
                risk,
                "risk_level",
                "",
            )
        )
        .lower()
        .strip()
    )


    if risk_level not in VALID_RISK_LEVELS:
        raise ValueError(
            f"Invalid risk level: {risk_level}"
        )


    score = getattr(
        risk,
        "risk_score",
        None,
    )


    if not isinstance(
        score,
        (int, float),
    ):
        raise TypeError(
            "risk_score must be numeric."
        )


    if not 0 <= score <= 100:
        raise ValueError(
            "risk_score must be between 0 and 100."
        )


    return risk_level


def _get_confidence(
    risk,
):
    """
    Read and validate backend confidence.

    Confidence remains backend-owned.

    Missing confidence is allowed for compatibility,
    but if provided it must be between 0 and 1.
    """

    confidence = getattr(
        risk,
        "confidence",
        None,
    )


    if confidence is None:
        return None


    if not isinstance(
        confidence,
        (int, float),
    ):
        raise TypeError(
            "confidence must be numeric."
        )


    if not 0 <= confidence <= 1:
        raise ValueError(
            "confidence must be between 0 and 1."
        )


    return float(
        confidence
    )


def _safe_text(
    value,
    default,
) -> str:
    """
    Safely convert a value to text.
    """

    if value is None:
        return default


    text = str(
        value
    ).strip()


    return (
        text
        if text
        else default
    )


# ============================================================
# BUILD AI PAYLOAD
# ============================================================


def build_ai_payload(
    assessment,
    accessibility=None,
    language="en",
) -> dict:
    """
    Convert MONJED backend assessment
    into a controlled AI communication payload.

    Gemini receives approved backend outputs only.

    Scientific risk and operational decisions
    remain backend-owned.
    """


    # --------------------------------------------------------
    # Validate assessment structure
    # --------------------------------------------------------

    if not hasattr(
        assessment,
        "risk",
    ):
        raise TypeError(
            "Invalid MONJED assessment object: risk is missing."
        )


    if not hasattr(
        assessment,
        "decision",
    ):
        raise TypeError(
            "Invalid MONJED assessment object: decision is missing."
        )


    risk = assessment.risk

    decision = assessment.decision


    # --------------------------------------------------------
    # Validate backend scientific risk
    # --------------------------------------------------------

    risk_level = _validate_risk(
        risk
    )


    risk_confidence = _get_confidence(
        risk
    )


    language = _validate_language(
        language
    )


    # --------------------------------------------------------
    # Backend decision remains source of truth
    # --------------------------------------------------------

    current_action = _safe_text(
        getattr(
            decision,
            "current_action",
            None,
        ),
        "Follow official safety guidance.",
    )


    backup_action = _safe_text(
        getattr(
            decision,
            "backup_action",
            None,
        ),
        "Follow local authority instructions.",
    )


    decision_status = _safe_text(
        getattr(
            decision,
            "decision_status",
            None,
        ),
        "no_adjustment",
    )


    notification_required = bool(
        getattr(
            decision,
            "notification_required",
            False,
        )
    )


    # --------------------------------------------------------
    # Accessibility layer
    # --------------------------------------------------------

    accessibility_needs = []

    accessibility_instructions = []


    if accessibility:

        accessibility_needs = (
            _validate_accessibility_needs(
                getattr(
                    accessibility,
                    "accessibility_needs",
                    [],
                )
            )
        )


        accessibility_instructions = deepcopy(
            getattr(
                accessibility,
                "communication_requirements",
                [],
            )
        )


    # --------------------------------------------------------
    # Country
    # --------------------------------------------------------

    country = getattr(
        assessment,
        "country",
        None,
    )


    if country is None:

        country = getattr(
            risk,
            "country",
            DEFAULT_COUNTRY,
        )


    country = _safe_text(
        country,
        DEFAULT_COUNTRY,
    )


    # --------------------------------------------------------
    # Zone
    # --------------------------------------------------------

    zone_id = _safe_text(
        getattr(
            risk,
            "zone_id",
            None,
        ),
        "UNKNOWN",
    )


    # --------------------------------------------------------
    # Final controlled AI payload
    # --------------------------------------------------------

    return {

        "source":
            "MONJED_BACKEND",


        "ai_role":
            "communication_only",


        "generated_by":
            "MONJED_DECISION_ENGINE",


        "zone_id":
            zone_id,


        "country":
            country,


        "language":
            language,


        # ====================================================
        # SCIENTIFIC RISK — BACKEND OWNED
        # ====================================================

        "hazards": [
            {
                "hazard":
                    getattr(
                        risk,
                        "hazard",
                        "unknown",
                    ),

                "risk_score":
                    risk.risk_score,

                "risk_level":
                    risk_level,

                "confidence":
                    risk_confidence,

                "reasons":
                    deepcopy(
                        getattr(
                            risk,
                            "reasons",
                            [],
                        )
                    ),
            }
        ],


        # ====================================================
        # COMMUNITY OPERATIONAL EVIDENCE
        # ====================================================

        "community_evidence": {
            "matching_reports":
                max(
                    0,
                    getattr(
                        decision,
                        "evidence_used",
                        0,
                    ),
                )
        },


        # ====================================================
        # DETERMINISTIC BACKEND DECISION
        # ====================================================

        "decision": {

            "decision_status":
                decision_status,

            "notification_required":
                notification_required,

            "current_action":
                current_action,

            "backup_action":
                backup_action,

            "accessibility_instructions":
                deepcopy(
                    accessibility_instructions
                ),
        },


        # ====================================================
        # ACCESSIBILITY
        # ====================================================

        "accessibility_needs":
            accessibility_needs,


        # ====================================================
        # CONFIDENCE METADATA
        # ====================================================

        "confidence": {
            "source":
                "backend",
        },
    }