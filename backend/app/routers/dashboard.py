from fastapi import (
    APIRouter,
    Query,
)

from database.connection import (
    get_database,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


def _clean_document(
    document,
):

    if document is None:
        return None

    document = dict(
        document
    )

    document.pop(
        "_id",
        None,
    )

    return document


def _clean_documents(
    documents,
):

    return [
        _clean_document(
            document
        )
        for document in documents
    ]


@router.get(
    "/overview"
)
def dashboard_overview():

    db = get_database()

    latest_risks = {}

    cursor = (
        db[
            "risk_snapshots"
        ]
        .find()
        .sort(
            "created_at",
            -1,
        )
        .limit(
            500
        )
    )

    for document in cursor:

        key = (
            document.get(
                "zone_id"
            ),
            document.get(
                "hazard"
            ),
        )

        if key not in latest_risks:

            latest_risks[
                key
            ] = document

    risk_levels = {
        "unknown":
            0,
        "low":
            0,
        "moderate":
            0,
        "high":
            0,
        "critical":
            0,
    }

    for document in (
        latest_risks.values()
    ):

        level = str(
            document.get(
                "risk_level",
                "unknown",
            )
        ).lower()

        if level not in risk_levels:
            level = "unknown"

        risk_levels[
            level
        ] += 1

    return {

        "status":
            "ok",

        "latest_risk_assessments":
            len(
                latest_risks
            ),

        "risk_levels":
            risk_levels,

        "active_notifications":
            db[
                "alerts"
            ].count_documents(
                {
                    "notification_required":
                        True
                }
            ),

        "human_review_cases":
            db[
                "decisions"
            ].count_documents(
                {
                    "decision_status":
                        "human_review_required"
                }
            ),

        "community_reports":
            db[
                "community_reports"
            ].count_documents(
                {}
            ),

        "registered_users":
            db[
                "users"
            ].count_documents(
                {}
            ),

        "zones":
            db[
                "zones"
            ].count_documents(
                {}
            ),
    }


@router.get(
    "/risks"
)
def dashboard_risks(
    zone_id: str | None = None,
    hazard: str | None = None,
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
):

    db = get_database()

    query = {}

    if zone_id:
        query[
            "zone_id"
        ] = zone_id

    if hazard:
        query[
            "hazard"
        ] = hazard

    documents = (
        db[
            "risk_snapshots"
        ]
        .find(
            query
        )
        .sort(
            "created_at",
            -1,
        )
        .limit(
            limit
        )
    )

    return _clean_documents(
        documents
    )


@router.get(
    "/decisions"
)
def dashboard_decisions(
    zone_id: str | None = None,
    hazard: str | None = None,
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
):

    db = get_database()

    query = {}

    if zone_id:
        query[
            "zone_id"
        ] = zone_id

    if hazard:
        query[
            "hazard"
        ] = hazard

    documents = (
        db[
            "decisions"
        ]
        .find(
            query
        )
        .sort(
            "created_at",
            -1,
        )
        .limit(
            limit
        )
    )

    return _clean_documents(
        documents
    )


@router.get(
    "/alerts"
)
def dashboard_alerts(
    zone_id: str | None = None,
    hazard: str | None = None,
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
):

    db = get_database()

    query = {}

    if zone_id:
        query[
            "zone_id"
        ] = zone_id

    if hazard:
        query[
            "hazard"
        ] = hazard

    documents = (
        db[
            "alerts"
        ]
        .find(
            query
        )
        .sort(
            "created_at",
            -1,
        )
        .limit(
            limit
        )
    )

    return _clean_documents(
        documents
    )


@router.get(
    "/zones/{zone_id}"
)
def dashboard_zone(
    zone_id: str,
):

    db = get_database()

    risks_cursor = (
        db[
            "risk_snapshots"
        ]
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

    latest_risks = {}

    for document in risks_cursor:

        hazard = document.get(
            "hazard",
            "unknown",
        )

        if hazard not in latest_risks:

            latest_risks[
                hazard
            ] = _clean_document(
                document
            )

    latest_decision = (
        db[
            "decisions"
        ]
        .find_one(
            {
                "zone_id":
                    zone_id
            },
            sort=[
                (
                    "created_at",
                    -1,
                )
            ],
        )
    )

    latest_alert = (
        db[
            "alerts"
        ]
        .find_one(
            {
                "zone_id":
                    zone_id
            },
            sort=[
                (
                    "created_at",
                    -1,
                )
            ],
        )
    )

    recent_reports = (
        db[
            "community_reports"
        ]
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
            20
        )
    )

    return {

        "zone_id":
            zone_id,

        "risks":
            latest_risks,

        "latest_decision":
            _clean_document(
                latest_decision
            ),

        "latest_alert":
            _clean_document(
                latest_alert
            ),

        "recent_community_reports":
            _clean_documents(
                recent_reports
            ),
    }


@router.get(
    "/recipients/count"
)
def recipient_count(
    zone_id: str,
):

    db = get_database()

    count = db[
        "users"
    ].count_documents(
        {
            "zone_id":
                zone_id,

            "$or": [
                {
                    "notification_consent":
                        True
                },
                {
                    "notifications_enabled":
                        True
                },
            ],
        }
    )

    return {
        "zone_id":
            zone_id,

        "eligible_recipient_count":
            count,
    }