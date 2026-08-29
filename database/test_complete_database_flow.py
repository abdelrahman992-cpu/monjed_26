"""
MONJED Database End-to-End Test

Tests:

MongoDB Connection
        ↓
Indexes
        ↓
Risk Snapshot
        ↓
Deterministic Decision
        ↓
Normalized Alert
        ↓
Delivery Result
        ↓
Read Back
        ↓
Cleanup


IMPORTANT:
- Uses dedicated test identifiers.
- Does not modify scientific risk.
- Does not run Gemini.
- Does not send a real SMS.
- Cleans test data after completion.
"""


import json
from uuid import uuid4


from database.connection import (
    get_database,
    close_connection,
)

from database.indexes import (
    create_indexes,
)

from database.risk_repository import (
    create_risk_snapshot,
    get_risk_snapshot,
    get_latest_risk,
    delete_risk_snapshot,
)

from database.decision_repository import (
    create_decision,
    get_decision,
    get_latest_decision,
    get_decision_collection,
)

from database.alerts_repository import (
    create_alert,
    get_alert,
    get_alerts_collection,
)


# ============================================================
# HELPERS
# ============================================================


def print_section(
    title: str,
    data,
):
    print(
        f"\n========== {title} =========="
    )

    print(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
            default=str,
        )
    )


# ============================================================
# TEST IDENTIFIERS
# ============================================================


test_id = str(uuid4())[:8]

ZONE_ID = f"db_test_zone_{test_id}"

COUNTRY = "Kenya"

HAZARD = "flood"


created_risk_id = None
created_decision_id = None
created_alert_id = None


try:

    # ========================================================
    # 1. DATABASE CONNECTION
    # ========================================================

    db = get_database()

    assert db is not None, (
        "MongoDB database connection is None."
    )

    db.command(
        "ping"
    )

    print(
        "\nMongoDB connection test: PASSED"
    )


    # ========================================================
    # 2. INDEXES
    # ========================================================

    create_indexes()

    print(
        "MongoDB indexes test: PASSED"
    )


    # ========================================================
    # 3. RISK SNAPSHOT
    # ========================================================

    risk_data = {

        "zone_id":
            ZONE_ID,

        "country":
            COUNTRY,

        "hazard":
            HAZARD,

        "risk_score":
            75.0,

        "risk_level":
            "high",

        "confidence":
            0.85,

        "reasons": [
            (
                "Heavy rainfall detected and "
                "water levels are increasing."
            )
        ],

        "data_source":
            "TEST_SOURCE",

        "data_available":
            True,

        "features": {
            "test":
                True
        },
    }


    created_risk_id = create_risk_snapshot(
        risk_data
    )


    assert created_risk_id, (
        "Risk repository did not return risk_id."
    )


    stored_risk = get_risk_snapshot(
        created_risk_id
    )


    assert stored_risk is not None, (
        "Risk snapshot was not stored."
    )


    assert stored_risk[
        "risk_score"
    ] == 75.0


    assert stored_risk[
        "risk_level"
    ] == "high"


    assert stored_risk[
        "confidence"
    ] == 0.85


    assert stored_risk[
        "hazard"
    ] == HAZARD


    assert stored_risk[
        "zone_id"
    ] == ZONE_ID


    latest_risk = get_latest_risk(
        ZONE_ID,
        HAZARD,
    )


    assert latest_risk is not None


    assert latest_risk[
        "risk_id"
    ] == created_risk_id


    print_section(
        "STORED RISK",
        stored_risk,
    )


    # ========================================================
    # 4. DETERMINISTIC DECISION
    # ========================================================

    decision_data = {

        "risk_id":
            created_risk_id,

        "zone_id":
            ZONE_ID,

        "hazard":
            HAZARD,

        "risk_score":
            75.0,

        "risk_level":
            "high",

        "confidence":
            0.85,

        "decision_status":
            "action_adjusted",

        "notification_required":
            True,

        "current_action":
            (
                "Move to a safer elevated area "
                "and avoid affected locations."
            ),

        "backup_action":
            (
                "Follow local authority instructions."
            ),

        "reasons": [
            (
                "Risk level requires "
                "action adjustment."
            )
        ],

        "evidence_used":
            0,

        "source_report_ids":
            [],
    }


    stored_decision = create_decision(
        decision_data
    )


    assert stored_decision is not None


    created_decision_id = stored_decision[
        "decision_id"
    ]


    assert stored_decision[
        "risk_id"
    ] == created_risk_id


    assert stored_decision[
        "risk_score"
    ] == stored_risk[
        "risk_score"
    ]


    assert stored_decision[
        "risk_level"
    ] == stored_risk[
        "risk_level"
    ]


    assert stored_decision[
        "confidence"
    ] == stored_risk[
        "confidence"
    ]


    assert stored_decision[
        "notification_required"
    ] is True


    fetched_decision = get_decision(
        created_decision_id
    )


    assert fetched_decision is not None


    latest_decision = get_latest_decision(
        ZONE_ID,
        HAZARD,
    )


    assert latest_decision is not None


    assert latest_decision[
        "decision_id"
    ] == created_decision_id


    print_section(
        "STORED DECISION",
        stored_decision,
    )


    # ========================================================
    # 5. NORMALIZED ALERT
    # ========================================================

    normalized_alert = {

        "title":
            "MONJED Alert",

        "zone_id":
            ZONE_ID,

        "country":
            COUNTRY,

        "language":
            "en",

        "hazards": [
            {
                "type":
                    HAZARD,

                "risk_level":
                    "high",

                "risk_score":
                    75.0,

                "confidence":
                    0.85,

                "message":
                    (
                        "Heavy rainfall detected and "
                        "water levels are increasing."
                    ),
            }
        ],

        "community_evidence_summary":
            (
                "No recent community evidence items "
                "were used in the operational decision."
            ),

        "final_decision": {

            "decision_status":
                "action_adjusted",

            "notification_required":
                True,

            "current_action":
                (
                    "Move to a safer elevated area "
                    "and avoid affected locations."
                ),

            "backup_action":
                (
                    "Follow local authority instructions."
                ),

            "accessibility_instructions":
                [],
        },

        "notification_required":
            True,

        "accessibility_needs":
            [],

        "alert_message":
            (
                "High flood risk detected. "
                "Follow the approved action."
            ),

        "alert_source":
            "DETERMINISTIC_FALLBACK",
    }


    # ========================================================
    # 6. DELIVERY RESULT
    # ========================================================

    delivery_result = {

        "notification_required":
            True,

        "dashboard": {
            "success":
                True
        },

        "sms": [
            {
                "phone":
                    "+20XXXXXXXXXX",

                "result": {
                    "success":
                        False,

                    "provider":
                        "AFRICAS_TALKING",

                    "test":
                        True,
                },
            }
        ],

        "voice": {

            "success":
                True,

            "provider":
                "MOCK_TTS",

            "delivery_status":
                "simulated",
        },
    }


    # ========================================================
    # 7. STORE ALERT
    # ========================================================

    stored_alert = create_alert(

        normalized_alert,

        delivery_result=
            delivery_result,
    )


    assert stored_alert is not None


    created_alert_id = stored_alert[
        "alert_id"
    ]


    assert stored_alert[
        "hazard"
    ] == HAZARD


    assert stored_alert[
        "risk_score"
    ] == 75.0


    assert stored_alert[
        "risk_level"
    ] == "high"


    assert stored_alert[
        "confidence"
    ] == 0.85


    assert stored_alert[
        "decision_status"
    ] == "action_adjusted"


    assert stored_alert[
        "notification_required"
    ] is True


    assert stored_alert[
        "alert_source"
    ] == "DETERMINISTIC_FALLBACK"


    assert stored_alert[
        "delivery"
    ][
        "voice"
    ][
        "provider"
    ] == "MOCK_TTS"


    fetched_alert = get_alert(
        created_alert_id
    )


    assert fetched_alert is not None


    assert fetched_alert[
        "alert_id"
    ] == created_alert_id


    print_section(
        "STORED ALERT",
        stored_alert,
    )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    print(
        "\n"
        "============================================\n"
        "MONJED DATABASE E2E TEST PASSED\n"
        "============================================"
    )


finally:

    # ========================================================
    # CLEANUP TEST DATA
    # ========================================================

    print(
        "\nCleaning database test records..."
    )


    try:

        if created_alert_id:

            get_alerts_collection().delete_one(
                {
                    "alert_id":
                        created_alert_id
                }
            )


        if created_decision_id:

            get_decision_collection().delete_one(
                {
                    "decision_id":
                        created_decision_id
                }
            )


        if created_risk_id:

            delete_risk_snapshot(
                created_risk_id
            )


        print(
            "Database test cleanup: COMPLETED"
        )


    finally:

        close_connection()