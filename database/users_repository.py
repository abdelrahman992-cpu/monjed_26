from database.connection import get_database


# ============================================================
# COLLECTION
# ============================================================

def get_users_collection():

    db = get_database()

    return db["users"]


# ============================================================
# CREATE
# ============================================================

def create_user(
    data,
):

    collection = get_users_collection()

    collection.insert_one(
        data
    )

    return data[
        "user_id"
    ]


# ============================================================
# GET BY USER ID
# ============================================================

def get_user(
    user_id,
):

    collection = get_users_collection()

    return collection.find_one(
        {
            "user_id":
                user_id
        }
    )


# ============================================================
# GET BY EMAIL
# ============================================================

def get_user_by_email(
    email,
):

    if not email:
        return None

    normalized_email = str(
        email
    ).strip().lower()

    if not normalized_email:
        return None

    collection = get_users_collection()

    return collection.find_one(
        {
            "$or": [
                {
                    "email":
                        normalized_email
                },
                {
                    "work_email":
                        normalized_email
                },
            ]
        }
    )


# ============================================================
# GET BY PHONE
# ============================================================

def get_user_by_phone(
    phone,
):

    if not phone:
        return None

    normalized_phone = str(
        phone
    ).strip()

    if not normalized_phone:
        return None

    collection = get_users_collection()

    return collection.find_one(
        {
            "$or": [
                {
                    "phone":
                        normalized_phone
                },
                {
                    "phone_number":
                        normalized_phone
                },
            ]
        }
    )


# ============================================================
# ALL USERS
# ============================================================

def get_all_users():

    collection = get_users_collection()

    return list(
        collection.find()
    )


# ============================================================
# USERS BY ZONE
# ============================================================

def get_users_by_zone(
    zone_id,
):

    collection = get_users_collection()

    return list(
        collection.find(
            {
                "zone_id":
                    zone_id
            }
        )
    )


# ============================================================
# ALERT RECIPIENTS
# ============================================================

def get_alert_recipients_by_zone(
    zone_id,
):
    """
    Return users who explicitly consented to notifications
    and have a valid stored phone number.

    Supports both:
    - phone
    - phone_number

    for compatibility with existing records.
    """

    collection = get_users_collection()

    users = list(
        collection.find(
            {
                "zone_id":
                    zone_id,

                "$and": [

                    {
                        "$or": [
                            {
                                "notification_consent":
                                    True
                            },
                            {
                                "notifications_enabled":
                                    True
                            },
                        ]
                    },

                    {
                        "$or": [
                            {
                                "phone": {
                                    "$exists":
                                        True,
                                    "$nin": [
                                        None,
                                        "",
                                    ],
                                }
                            },
                            {
                                "phone_number": {
                                    "$exists":
                                        True,
                                    "$nin": [
                                        None,
                                        "",
                                    ],
                                }
                            },
                        ]
                    },
                ]
            }
        )
    )

    recipients = []

    for user in users:

        phone = (
            user.get(
                "phone"
            )
            or user.get(
                "phone_number"
            )
        )

        if not phone:
            continue

        recipients.append(
            {
                "user_id":
                    user.get(
                        "user_id"
                    ),

                "phone":
                    phone,

                "zone_id":
                    user.get(
                        "zone_id"
                    ),

                "preferred_language":
                    user.get(
                        "preferred_language",
                        "en",
                    ),

                "accessibility_needs":
                    user.get(
                        "accessibility_needs",
                        [],
                    ),
            }
        )

    return recipients


# ============================================================
# PHONE NUMBERS ONLY
# Legacy compatibility helper
# ============================================================

def get_recipient_phone_numbers(
    zone_id,
):

    recipients = (
        get_alert_recipients_by_zone(
            zone_id
        )
    )

    numbers = []

    for recipient in recipients:

        phone = recipient[
            "phone"
        ]

        if phone not in numbers:

            numbers.append(
                phone
            )

    return numbers


# ============================================================
# UPDATE
# ============================================================

def update_user(
    user_id,
    data,
):

    collection = get_users_collection()

    result = collection.update_one(
        {
            "user_id":
                user_id
        },
        {
            "$set":
                data
        }
    )

    return result.modified_count


# ============================================================
# DELETE
# ============================================================

def delete_user(
    user_id,
):

    collection = get_users_collection()

    result = collection.delete_one(
        {
            "user_id":
                user_id
        }
    )

    return result.deleted_count
