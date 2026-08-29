"""
MONJED Risk Repository

Persists scientific hazard risk snapshots.

Flood and earthquake risk remain independent.
Community evidence never modifies these records.
"""


from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from database.connection import get_database


def get_risk_collection():
    return get_database()["risk_snapshots"]


def create_risk_snapshot(data: dict) -> str:
    """
    Store one scientific risk assessment.

    Returns:
        generated risk_id
    """

    if not isinstance(data, dict):
        raise TypeError(
            "Risk snapshot must be a dictionary."
        )

    required_fields = {
    "zone_id",
    "hazard",
    "risk_score",
    "risk_level",
    "confidence",
    }

    missing = [
        field
        for field in required_fields
        if field not in data
    ]

    if missing:
        raise ValueError(
            f"Missing risk fields: {', '.join(missing)}"
        )

    snapshot = deepcopy(data)

    snapshot.setdefault(
        "risk_id",
        str(uuid4()),
    )

    snapshot.setdefault(
        "created_at",
        datetime.now(
            timezone.utc
        ),
    )

    get_risk_collection().insert_one(
        snapshot
    )

    return snapshot["risk_id"]


def get_risk_snapshot(
    risk_id: str,
):
    return get_risk_collection().find_one(
        {
            "risk_id": risk_id
        }
    )


def get_latest_risk(
    zone_id: str,
    hazard: str,
):
    """
    Return latest risk for one hazard in one zone.

    Flood and earthquake are queried separately.
    """

    return get_risk_collection().find_one(
        {
            "zone_id": zone_id,
            "hazard": hazard,
        },
        sort=[
            ("created_at", -1)
        ],
    )


def get_all_risk_snapshots():
    return list(
        get_risk_collection()
        .find()
        .sort(
            "created_at",
            -1,
        )
    )


def delete_risk_snapshot(
    risk_id: str,
) -> int:

    result = (
        get_risk_collection()
        .delete_one(
            {
                "risk_id": risk_id
            }
        )
    )

    return result.deleted_count