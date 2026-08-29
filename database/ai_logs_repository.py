"""
MONJED AI Logs Repository

Stores audit logs for MONJED AI communication activity.

Examples:
- Gemini communication attempts
- Deterministic fallback output
- AI validation results
- Communication pipeline metadata

IMPORTANT:
- Does NOT calculate risk.
- Does NOT make decisions.
- Does NOT modify backend-approved actions.
- Does NOT modify scientific confidence.
- This repository is for observability and auditing only.
"""


from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from database.connection import get_database


# ============================================================
# CONSTANTS
# ============================================================


DEFAULT_LIMIT = 100
MAX_LIMIT = 500


# ============================================================
# COLLECTION
# ============================================================


def get_ai_logs_collection():
    """
    Return the MONJED AI logs collection.

    Database access happens at call time rather than
    module import time so MongoDB can connect safely.
    """

    return get_database()["ai_logs"]


# ============================================================
# HELPERS
# ============================================================


def _clean_text(
    value,
    default="",
) -> str:
    """
    Safely normalize a text value.
    """

    if value is None:
        return default

    text = str(value).strip()

    return text if text else default


def _normalize_limit(
    limit,
) -> int:
    """
    Validate query limit and protect against
    unnecessarily large MongoDB reads.
    """

    if not isinstance(
        limit,
        int,
    ):
        return DEFAULT_LIMIT

    if limit <= 0:
        return DEFAULT_LIMIT

    return min(
        limit,
        MAX_LIMIT,
    )


# ============================================================
# CREATE
# ============================================================


def create_ai_log(
    log_data: dict,
):
    """
    Store one AI communication/audit log.

    Supported fields include:

    - model
    - provider
    - source
    - ai_role
    - generated_by
    - alert_source
    - zone_id
    - country
    - language
    - input
    - output
    - confidence
    - validation
    - success
    - error

    Returns:
        inserted MongoDB document
    """

    if not isinstance(
        log_data,
        dict,
    ):
        raise TypeError(
            "AI log data must be a dictionary."
        )


    # --------------------------------------------------------
    # Model / Provider identification
    # --------------------------------------------------------

    model = _clean_text(
        log_data.get(
            "model"
        ),
        "UNKNOWN",
    )


    provider = _clean_text(
        log_data.get(
            "provider"
        )
    )


    # --------------------------------------------------------
    # Build audit document
    # --------------------------------------------------------

    log = {

        "log_id":
            log_data.get(
                "log_id",
                str(uuid4()),
            ),

        "model":
            model,

        "provider":
            provider,

        "source":
            _clean_text(
                log_data.get(
                    "source"
                )
            ),

        "ai_role":
            _clean_text(
                log_data.get(
                    "ai_role"
                ),
                "communication_only",
            ),

        "generated_by":
            _clean_text(
                log_data.get(
                    "generated_by"
                )
            ),

        "alert_source":
            _clean_text(
                log_data.get(
                    "alert_source"
                )
            ),

        "zone_id":
            _clean_text(
                log_data.get(
                    "zone_id"
                )
            ),

        "country":
            _clean_text(
                log_data.get(
                    "country"
                )
            ),

        "language":
            _clean_text(
                log_data.get(
                    "language"
                ),
                "en",
            ).lower(),

        # ----------------------------------------------------
        # Communication input/output
        # ----------------------------------------------------

        "input":
            deepcopy(
                log_data.get(
                    "input",
                    {},
                )
            ),

        "output":
            deepcopy(
                log_data.get(
                    "output",
                    {},
                )
            ),

        # ----------------------------------------------------
        # Backend-owned confidence metadata
        # ----------------------------------------------------

        "confidence":
            deepcopy(
                log_data.get(
                    "confidence"
                )
            ),

        # ----------------------------------------------------
        # Validation / execution result
        # ----------------------------------------------------

        "validation":
            deepcopy(
                log_data.get(
                    "validation",
                    {},
                )
            ),

        "success":
            bool(
                log_data.get(
                    "success",
                    True,
                )
            ),

        "error":
            _clean_text(
                log_data.get(
                    "error"
                )
            ),

        # ----------------------------------------------------
        # Timing
        # ----------------------------------------------------

        "generated_at":
            log_data.get(
                "generated_at"
            ),

        "created_at":
            datetime.now(
                timezone.utc
            ),
    }


    # --------------------------------------------------------
    # Insert
    # --------------------------------------------------------

    collection = get_ai_logs_collection()


    result = collection.insert_one(
        log
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


def get_ai_log(
    log_id: str,
):
    """
    Return one AI log by MONJED log_id.
    """

    clean_log_id = _clean_text(
        log_id
    )


    if not clean_log_id:
        return None


    return get_ai_logs_collection().find_one(
        {
            "log_id":
                clean_log_id
        }
    )


# ============================================================
# QUERY BY MODEL
# ============================================================


def get_ai_logs_by_model(
    model: str,
    limit: int = DEFAULT_LIMIT,
):
    """
    Return newest logs for a specific AI model.
    """

    clean_model = _clean_text(
        model
    )


    if not clean_model:
        return []


    limit = _normalize_limit(
        limit
    )


    return list(
        get_ai_logs_collection()
        .find(
            {
                "model":
                    clean_model
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
# QUERY BY ZONE
# ============================================================


def get_ai_logs_by_zone(
    zone_id: str,
    limit: int = DEFAULT_LIMIT,
):
    """
    Return newest AI communication logs
    associated with a MONJED zone.
    """

    clean_zone_id = _clean_text(
        zone_id
    )


    if not clean_zone_id:
        return []


    limit = _normalize_limit(
        limit
    )


    return list(
        get_ai_logs_collection()
        .find(
            {
                "zone_id":
                    clean_zone_id
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
# RECENT LOGS
# ============================================================


def get_recent_ai_logs(
    limit: int = DEFAULT_LIMIT,
):
    """
    Return newest MONJED AI logs.
    """

    limit = _normalize_limit(
        limit
    )


    return list(
        get_ai_logs_collection()
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
# DELETE
# ============================================================


def delete_ai_log(
    log_id: str,
) -> int:
    """
    Delete one AI log.

    Returns:
        number of deleted documents
    """

    clean_log_id = _clean_text(
        log_id
    )


    if not clean_log_id:
        return 0


    result = (
        get_ai_logs_collection()
        .delete_one(
            {
                "log_id":
                    clean_log_id
            }
        )
    )


    return result.deleted_count