"""
MONJED Decision Repository

Stores deterministic operational decisions.

IMPORTANT:
- Does NOT calculate risk.
- Does NOT modify scientific risk.
- Community evidence affects operational decisions only.
"""


from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from database.connection import get_database


def get_decision_collection():
    return get_database()["decisions"]


def create_decision(
    decision_data: dict,
):
    """
    Persist a MONJED deterministic decision.
    """

    if not isinstance(
        decision_data,
        dict,
    ):
        raise TypeError(
            "Decision must be a dictionary."
        )


    required_fields = {
        "zone_id",
        "hazard",
        "risk_score",
        "risk_level",
        "confidence",
        "decision_status",
    }


    missing = [
        field
        for field in required_fields
        if field not in decision_data
    ]


    if missing:
        raise ValueError(
            f"Missing decision fields: {', '.join(missing)}"
        )


    decision = {

        "decision_id":
            decision_data.get(
                "decision_id",
                str(uuid4()),
            ),

        # Optional relationship with persisted risk snapshot.
        "risk_id":
            decision_data.get(
                "risk_id"
            ),

        "zone_id":
            decision_data["zone_id"],

        "hazard":
            decision_data["hazard"],

        "risk_score":
            decision_data["risk_score"],

        "risk_level":
            decision_data["risk_level"],

        "confidence":
            decision_data["confidence"],

        "decision_status":
            decision_data[
                "decision_status"
            ],

        "notification_required":
            bool(
                decision_data.get(
                    "notification_required",
                    False,
                )
            ),

        "current_action":
            decision_data.get(
                "current_action",
                "",
            ),

        "backup_action":
            decision_data.get(
                "backup_action",
                "",
            ),

        "reasons":
            deepcopy(
                decision_data.get(
                    "reasons",
                    [],
                )
            ),

        "evidence_used":
            max(
                0,
                decision_data.get(
                    "evidence_used",
                    0,
                ),
            ),

        "source_report_ids":
            deepcopy(
                decision_data.get(
                    "source_report_ids",
                    [],
                )
            ),

        "evaluated_at":
            decision_data.get(
                "evaluated_at"
            ),

        "created_at":
            datetime.now(
                timezone.utc
            ),
    }


    result = (
        get_decision_collection()
        .insert_one(
            decision
        )
    )


    return (
        get_decision_collection()
        .find_one(
            {
                "_id":
                    result.inserted_id
            }
        )
    )


def get_decision(
    decision_id: str,
):
    return (
        get_decision_collection()
        .find_one(
            {
                "decision_id":
                    decision_id
            }
        )
    )


def get_decisions_by_zone(
    zone_id: str,
):
    return list(
        get_decision_collection()
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
    )


def get_latest_decision(
    zone_id: str,
    hazard: str,
):
    return (
        get_decision_collection()
        .find_one(
            {
                "zone_id":
                    zone_id,

                "hazard":
                    hazard,
            },
            sort=[
                (
                    "created_at",
                    -1,
                )
            ],
        )
    )