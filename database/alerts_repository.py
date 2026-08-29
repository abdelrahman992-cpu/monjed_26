"""
MONJED Alerts Repository

Persists normalized MONJED alerts and
their delivery results.

The alert repository stores the final alert
that reached the delivery layer.

IMPORTANT:
- Does NOT calculate risk.
- Does NOT make decisions.
- Does NOT modify backend-approved actions.
- Does NOT decide whether a notification is required.
"""

from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from database.connection import get_database


# ============================================================
# COLLECTION
# ============================================================

def get_alerts_collection():
    """
    Return MONJED alerts collection.
    """

    return get_database()["alerts"]


# ============================================================
# HELPERS
# ============================================================

def _safe_dict(value) -> dict:
    return value if isinstance(value, dict) else {}


def _safe_list(value) -> list:
    return value if isinstance(value, list) else []


def _clean_text(
    value,
    default="",
) -> str:

    if value is None:
        return default

    text = str(value).strip()

    return text if text else default


# ============================================================
# CREATE
# ============================================================

def create_alert(
    alert_data: dict,
    delivery_result: dict | None = None,
):
    """
    Store one normalized MONJED alert.

    Optional delivery_result may contain:
    - dashboard result
    - SMS results
    - voice result
    - notification_required

    Returns:
        inserted alert document
    """

    if not isinstance(
        alert_data,
        dict,
    ):
        raise TypeError(
            "Alert data must be a dictionary."
        )

    hazards = _safe_list(
        alert_data.get(
            "hazards",
            [],
        )
    )

    primary_hazard = _safe_dict(
        hazards[0]
        if hazards
        else {}
    )

    final_decision = _safe_dict(
        alert_data.get(
            "final_decision",
            {},
        )
    )

    delivery = _safe_dict(
        delivery_result
    )

    # --------------------------------------------------------
    # Backend-owned notification gate
    # --------------------------------------------------------

    notification_required = bool(
        alert_data.get(
            "notification_required",
            final_decision.get(
                "notification_required",
                False,
            ),
        )
    )

    # --------------------------------------------------------
    # Build persistent alert document
    # --------------------------------------------------------

    alert = {

        # ----------------------------------------------------
        # Traceability
        # ----------------------------------------------------

        "alert_id":
            alert_data.get(
                "alert_id",
                str(uuid4()),
            ),

        "risk_id":
            alert_data.get(
                "risk_id"
            ),

        "decision_id":
            alert_data.get(
                "decision_id"
            ),

        # ----------------------------------------------------
        # Location
        # ----------------------------------------------------

        "zone_id":
            _clean_text(
                alert_data.get(
                    "zone_id"
                ),
                "UNKNOWN",
            ),

        "country":
            _clean_text(
                alert_data.get(
                    "country"
                ),
                "UNKNOWN",
            ),

        "language":
            _clean_text(
                alert_data.get(
                    "language"
                ),
                "en",
            ).lower(),

        # ----------------------------------------------------
        # Primary hazard fields
        #
        # Stored at top level for efficient MongoDB queries.
        # Full hazards list is preserved below.
        # ----------------------------------------------------

        "hazard":
            _clean_text(
                primary_hazard.get(
                    "type"
                ),
                "unknown",
            ),

        "risk_level":
            _clean_text(
                primary_hazard.get(
                    "risk_level"
                ),
                "unknown",
            ),

        "risk_score":
            primary_hazard.get(
                "risk_score"
            ),

        "confidence":
            primary_hazard.get(
                "confidence"
            ),

        "hazards":
            deepcopy(
                hazards
            ),

        # ----------------------------------------------------
        # Decision
        # ----------------------------------------------------

        "decision_status":
            final_decision.get(
                "decision_status"
            ),

        "notification_required":
            notification_required,

        "current_action":
            final_decision.get(
                "current_action"
            ),

        "backup_action":
            final_decision.get(
                "backup_action"
            ),

        "final_decision":
            deepcopy(
                final_decision
            ),

        # ----------------------------------------------------
        # Communication
        # ----------------------------------------------------

        "title":
            _clean_text(
                alert_data.get(
                    "title"
                ),
                "MONJED Alert",
            ),

        "community_evidence_summary":
            _clean_text(
                alert_data.get(
                    "community_evidence_summary"
                )
            ),

        "alert_message":
            _clean_text(
                alert_data.get(
                    "alert_message"
                )
            ),

        "alert_source":
            _clean_text(
                alert_data.get(
                    "alert_source"
                ),
                "UNKNOWN",
            ),

        "accessibility_needs":
            deepcopy(
                _safe_list(
                    alert_data.get(
                        "accessibility_needs",
                        [],
                    )
                )
            ),

        # ----------------------------------------------------
        # Delivery
        # ----------------------------------------------------

        "delivery":
            deepcopy(
                delivery
            ),

        # ----------------------------------------------------
        # Timing
        # ----------------------------------------------------

        "generated_at":
            alert_data.get(
                "generated_at"
            ),

        "created_at":
            datetime.now(
                timezone.utc
            ),
    }

    collection = get_alerts_collection()

    result = collection.insert_one(
        alert
    )

    return collection.find_one(
        {
            "_id":
                result.inserted_id
        }
    )


# ============================================================
# GET BY ID
# ============================================================

def get_alert(
    alert_id: str,
):

    alert_id = _clean_text(
        alert_id
    )

    if not alert_id:
        return None

    return get_alerts_collection().find_one(
        {
            "alert_id":
                alert_id
        }
    )


# ============================================================
# GET BY ZONE
# ============================================================

def get_alerts_by_zone(
    zone_id: str,
    limit: int = 100,
):

    zone_id = _clean_text(
        zone_id
    )

    if not zone_id:
        return []

    limit = (
        limit
        if isinstance(limit, int)
        and 0 < limit <= 500
        else 100
    )

    return list(
        get_alerts_collection()
        .find(
            {
                "zone_id":
                    zone_id
            }
        )
        .sort(
            "created_at",
            -1,
        )
        .limit(
            limit
        )
    )


# ============================================================
# GET BY HAZARD
# ============================================================

def get_alerts_by_hazard(
    hazard: str,
    limit: int = 100,
):

    hazard = _clean_text(
        hazard
    ).lower()

    if not hazard:
        return []

    limit = (
        limit
        if isinstance(limit, int)
        and 0 < limit <= 500
        else 100
    )

    return list(
        get_alerts_collection()
        .find(
            {
                "hazard":
                    hazard
            }
        )
        .sort(
            "created_at",
            -1,
        )
        .limit(
            limit
        )
    )


# ============================================================
# RECENT ALERTS
# ============================================================

def get_all_alerts(
    limit: int = 100,
):

    limit = (
        limit
        if isinstance(limit, int)
        and 0 < limit <= 500
        else 100
    )

    return list(
        get_alerts_collection()
        .find()
        .sort(
            "created_at",
            -1,
        )
        .limit(
            limit
        )
    )


# ============================================================
# UPDATE DELIVERY RESULT
# ============================================================

def update_alert_delivery(
    alert_id: str,
    delivery_result: dict,
) -> int:
    """
    Update only delivery information.

    Scientific risk and deterministic decision
    are intentionally protected from this function.
    """

    if not isinstance(
        delivery_result,
        dict,
    ):
        raise TypeError(
            "delivery_result must be a dictionary."
        )

    result = (
        get_alerts_collection()
        .update_one(
            {
                "alert_id":
                    alert_id
            },
            {
                "$set": {
                    "delivery":
                        deepcopy(
                            delivery_result
                        ),

                    "delivery_updated_at":
                        datetime.now(
                            timezone.utc
                        ),
                }
            },
        )
    )

    return result.modified_count


# ============================================================
# DELETE
# ============================================================

def delete_alert(
    alert_id: str,
) -> int:

    result = (
        get_alerts_collection()
        .delete_one(
            {
                "alert_id":
                    alert_id
            }
        )
    )

    return result.deleted_count