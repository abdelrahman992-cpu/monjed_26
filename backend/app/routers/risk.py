from datetime import datetime
from fastapi import APIRouter, HTTPException

from database.risk_repository import (
    get_all_risk_snapshots,
)


router = APIRouter(
    prefix="/api/risk",
    tags=["Risk"],
)


def _serialize_snapshot(snapshot: dict) -> dict:
    """
    Convert MongoDB risk snapshot into JSON-safe data.
    """

    result = dict(snapshot)

    # MongoDB ObjectId
    if "_id" in result:
        result["_id"] = str(result["_id"])

    # Datetime values
    for key, value in result.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()

    return result


@router.get("/")
def get_risk_snapshots():
    """
    Return all stored risk snapshots
    for the MONJED risk map.
    """

    try:
        snapshots = get_all_risk_snapshots()

        return [
            _serialize_snapshot(snapshot)
            for snapshot in snapshots
        ]

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to load risk snapshots: "
                f"{exc}"
            ),
        )
