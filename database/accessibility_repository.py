"""
MONJED Accessibility Repository
"""


from datetime import datetime, timezone
from uuid import uuid4

from database.connection import get_database


def get_accessibility_collection():
    return get_database()[
        "accessibility_profiles"
    ]


def create_accessibility_profile(
    profile_data: dict,
):

    if not isinstance(
        profile_data,
        dict,
    ):
        raise TypeError(
            "Accessibility profile must be a dictionary."
        )


    if not profile_data.get(
        "user_id"
    ):
        raise ValueError(
            "user_id is required."
        )


    profile = {

        "profile_id":
            str(uuid4()),

        "user_id":
            profile_data[
                "user_id"
            ],

        # Canonical MONJED field name.
        "accessibility_needs":
            profile_data.get(
                "accessibility_needs",
                profile_data.get(
                    "needs",
                    [],
                ),
            ),

        "preferred_language":
            profile_data.get(
                "preferred_language",
                "en",
            ),

        "communication_requirements":
            profile_data.get(
                "communication_requirements",
                profile_data.get(
                    "communication_methods",
                    [],
                ),
            ),

        "created_at":
            datetime.now(
                timezone.utc
            ),

        "updated_at":
            datetime.now(
                timezone.utc
            ),
    }


    result = (
        get_accessibility_collection()
        .insert_one(
            profile
        )
    )


    return (
        get_accessibility_collection()
        .find_one(
            {
                "_id":
                    result.inserted_id
            }
        )
    )


def get_profile_by_user(
    user_id: str,
):
    return (
        get_accessibility_collection()
        .find_one(
            {
                "user_id":
                    user_id
            }
        )
    )


def update_accessibility_profile(
    user_id: str,
    data: dict,
):

    if not isinstance(
        data,
        dict,
    ):
        raise TypeError(
            "Accessibility update must be a dictionary."
        )


    allowed_fields = {
        "accessibility_needs",
        "preferred_language",
        "communication_requirements",
    }


    update_data = {
        key: value
        for key, value in data.items()
        if key in allowed_fields
    }


    update_data[
        "updated_at"
    ] = datetime.now(
        timezone.utc
    )


    get_accessibility_collection().update_one(
        {
            "user_id":
                user_id
        },
        {
            "$set":
                update_data
        },
    )


    return get_profile_by_user(
        user_id
    )