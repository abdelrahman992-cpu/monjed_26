"""
MONJED - Core Persistence Service

Persists scientific risk assessments and deterministic
operational decisions.

IMPORTANT:
- Does NOT calculate risk.
- Does NOT modify risk.
- Does NOT modify decisions.
- Does NOT send alerts.
- Final normalized alerts and delivery results are stored
  separately by database.alerts_repository.
- Database failure must NOT suppress a safety-critical result.
"""

from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from database.connection import get_database


# ============================================================
# HELPERS
# ============================================================

def _utc_now():
    return datetime.now(timezone.utc)


def _to_dict(value):

    if value is None:
        return None

    if isinstance(value, dict):
        return deepcopy(value)

    if hasattr(value, "model_dump"):
        return value.model_dump(
            mode="python"
        )

    raise TypeError(
        f"Unsupported persistence object: "
        f"{type(value).__name__}"
    )


# ============================================================
# CORE ASSESSMENT PERSISTENCE
# ============================================================

def persist_assessment(
    assessment,
) -> dict:
    """
    Persist the scientific risk assessment and deterministic
    operational decision.

    Alert persistence intentionally happens AFTER:
    - normalization
    - recipient selection
    - delivery

    so only the final delivery-ready alert is stored.
    """

    db = get_database()

    now = _utc_now()

    # ========================================================
    # 1. RISK SNAPSHOT
    # ========================================================

    risk = _to_dict(
        assessment.risk
    )

    risk_id = (
        risk.get("risk_id")
        or str(uuid4())
    )

    risk_document = deepcopy(
        risk
    )

    risk_document["risk_id"] = (
        risk_id
    )

    risk_document.setdefault(
        "created_at",
        now,
    )

    db[
        "risk_snapshots"
    ].insert_one(
        risk_document
    )

    # ========================================================
    # 2. DETERMINISTIC DECISION
    # ========================================================

    decision = _to_dict(
        assessment.decision
    )

    decision_id = (
        decision.get("decision_id")
        or str(uuid4())
    )

    decision_document = deepcopy(
        decision
    )

    decision_document[
        "decision_id"
    ] = decision_id

    decision_document[
        "risk_id"
    ] = risk_id

    decision_document.setdefault(
        "created_at",
        now,
    )

    # --------------------------------------------------------
    # Accessibility metadata
    # --------------------------------------------------------

    accessible_action = _to_dict(
        getattr(
            assessment,
            "accessible_action",
            None,
        )
    )

    if accessible_action is not None:

        decision_document[
            "accessible_action"
        ] = accessible_action

    # --------------------------------------------------------
    # Human assistance metadata
    # --------------------------------------------------------

    assistance_request = _to_dict(
        getattr(
            assessment,
            "assistance_request",
            None,
        )
    )

    if assistance_request is not None:

        decision_document[
            "assistance_request"
        ] = assistance_request

    db[
        "decisions"
    ].insert_one(
        decision_document
    )

    return {
        "success":
            True,

        "risk_id":
            risk_id,

        "decision_id":
            decision_id,
    }


# ============================================================
# SAFE WRAPPER
# ============================================================

def safe_persist_assessment(
    assessment,
) -> dict:
    """
    Safe persistence wrapper.

    A MongoDB failure must not suppress an otherwise valid
    disaster assessment or active warning.
    """

    try:

        return persist_assessment(
            assessment
        )

    except Exception as exc:

        print(
            "MONJED persistence warning: "
            f"{type(exc).__name__}: {exc}"
        )

        return {
            "success":
                False,

            "risk_id":
                None,

            "decision_id":
                None,

            "error":
                type(exc).__name__,
        }