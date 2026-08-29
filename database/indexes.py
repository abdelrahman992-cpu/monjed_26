"""
MONJED MongoDB Indexes

Creates indexes required by MONJED repositories.

IMPORTANT:
- Flood and earthquake remain independent.
- Decisions and risk snapshots remain separate.
- Core historical records do not use TTL indexes.
"""


from database.connection import get_database


def create_indexes():
    """
    Create all MONJED MongoDB indexes.

    MongoDB create_index is safe to call repeatedly
    when the same index already exists.
    """

    db = get_database()


    # ========================================================
    # RISK SNAPSHOTS
    # ========================================================

    risk = db["risk_snapshots"]


    risk.create_index(
        [
            ("risk_id", 1),
        ],
        unique=True,
    )


    risk.create_index(
        [
            ("zone_id", 1),
            ("hazard", 1),
            ("created_at", -1),
        ]
    )


    risk.create_index(
        [
            ("created_at", -1),
        ]
    )


    # ========================================================
    # COMMUNITY REPORTS
    # ========================================================

    reports = db["community_reports"]


    reports.create_index(
        [
            ("zone_id", 1),
            ("created_at", -1),
        ]
    )


    reports.create_index(
        [
            ("hazard_type", 1),
        ]
    )


    # ========================================================
    # ASSISTANCE REQUESTS
    # ========================================================

    requests = db["assistance_requests"]


    requests.create_index(
        [
            ("zone_id", 1),
            ("status", 1),
        ]
    )


    requests.create_index(
        [
            ("priority", -1),
        ]
    )


    requests.create_index(
        [
            ("created_at", -1),
        ]
    )


    # ========================================================
    # VOLUNTEERS
    # ========================================================

    volunteers = db["volunteers"]


    volunteers.create_index(
        [
            ("zone_id", 1),
            ("available", 1),
        ]
    )

    # ========================================================
    # DETERMINISTIC DECISIONS
    # ========================================================

    decisions = db["decisions"]


    decisions.create_index(
        [
            ("decision_id", 1),
        ],
        unique=True,
    )


    decisions.create_index(
        [
            ("zone_id", 1),
            ("hazard", 1),
            ("created_at", -1),
        ]
    )


    decisions.create_index(
        [
            ("risk_id", 1),
        ]
    )


    decisions.create_index(
        [
            ("notification_required", 1),
            ("created_at", -1),
        ]
    )


# ========================================================
# ALERTS
# ========================================================

    alerts = db["alerts"]


    alerts.create_index(
        [
            ("alert_id", 1),
        ],
        unique=True,
    )


    alerts.create_index(
        [
            ("zone_id", 1),
            ("hazard", 1),
            ("created_at", -1),
        ]
    )


    alerts.create_index(
        [
            ("notification_required", 1),
            ("created_at", -1),
        ]
    )


    alerts.create_index(
        [
            ("alert_source", 1),
            ("created_at", -1),
        ]
    )

    # ========================================================
    # AI LOGS
    # ========================================================

    ai_logs = db["ai_logs"]


    ai_logs.create_index(
        [
            ("log_id", 1),
        ],
        unique=True,
    )


    ai_logs.create_index(
        [
            ("model", 1),
            ("created_at", -1),
        ]
    )


    ai_logs.create_index(
        [
            ("zone_id", 1),
            ("created_at", -1),
        ]
    )


    ai_logs.create_index(
        [
            ("alert_source", 1),
            ("created_at", -1),
        ]
    )


    # ========================================================
    # USERS
    # ========================================================

    users = db["users"]


    users.create_index(
        [
            ("phone", 1),
        ],
        unique=True,
    )


    # ========================================================
    # ZONES
    # ========================================================

    zones = db["zones"]


    zones.create_index(
        [
            ("zone_id", 1),
        ],
        unique=True,
    )


    zones.create_index(
        [
            ("country", 1),
            ("name", 1),
        ]
    )


    # ========================================================
    # TRANSLATIONS
    # ========================================================

    translations = db["translations"]


    translations.create_index(
        [
            ("key", 1),
            ("language", 1),
        ],
        unique=True,
    )


    translations.create_index(
        [
            ("language", 1),
        ]
    )


    # ========================================================
    # ACCESSIBILITY PROFILES
    # ========================================================

    accessibility = db[
        "accessibility_profiles"
    ]


    accessibility.create_index(
        [
            ("user_id", 1),
        ],
        unique=True,
    )


    print(
        "MONJED MongoDB indexes created successfully!"
    )