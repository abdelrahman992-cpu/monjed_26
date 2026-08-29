from datetime import datetime, timezone
from uuid import uuid4

from database.connection import get_database


def get_contacts_collection():

    db = get_database()

    return db["contact_messages"]


def save_contact_message(
    data: dict,
):

    collection = get_contacts_collection()

    now = datetime.now(
        timezone.utc
    )

    record = {
        "contact_id":
            str(uuid4()),

        "name":
            data["name"],

        "email":
            data["email"],

        "phone":
            data.get("phone"),

        "subject":
            data.get("subject"),

        "message":
            data["message"],

        "status":
            "received",

        "created_at":
            now,
    }

    collection.insert_one(
        record.copy()
    )

    return record
