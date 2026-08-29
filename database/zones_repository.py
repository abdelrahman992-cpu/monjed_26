"""
MONJED Zones Repository

Zones contain geographic metadata only.

Scientific risk belongs to risk_snapshots,
because every hazard is evaluated independently.
"""


from datetime import datetime, timezone
from uuid import uuid4

from database.connection import get_database


def get_zones_collection():
    return get_database()["zones"]


def create_zone(
    zone_data: dict,
):

    if not isinstance(
        zone_data,
        dict,
    ):
        raise TypeError(
            "Zone data must be a dictionary."
        )


    if not zone_data.get(
        "name"
    ):
        raise ValueError(
            "Zone name is required."
        )


    if not zone_data.get(
        "country"
    ):
        raise ValueError(
            "Zone country is required."
        )


    zone = {

        "zone_id":
            zone_data.get(
                "zone_id",
                str(uuid4()),
            ),

        "name":
            zone_data[
                "name"
            ],

        "country":
            zone_data[
                "country"
            ],

        "coordinates":
            zone_data.get(
                "coordinates"
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
        get_zones_collection()
        .insert_one(
            zone
        )
    )


    return (
        get_zones_collection()
        .find_one(
            {
                "_id":
                    result.inserted_id
            }
        )
    )


def get_zone(
    zone_id: str,
):
    return (
        get_zones_collection()
        .find_one(
            {
                "zone_id":
                    zone_id
            }
        )
    )


def get_all_zones():
    return list(
        get_zones_collection()
        .find()
        .sort(
            "name",
            1,
        )
    )


def get_zones_by_country(
    country: str,
):
    return list(
        get_zones_collection()
        .find(
            {
                "country":
                    country
            }
        )
    )


def update_zone(
    zone_id: str,
    data: dict,
):

    if not isinstance(
        data,
        dict,
    ):
        raise TypeError(
            "Zone update must be a dictionary."
        )


    allowed_fields = {
        "name",
        "country",
        "coordinates",
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


    get_zones_collection().update_one(
        {
            "zone_id":
                zone_id
        },
        {
            "$set":
                update_data
        },
    )


    return get_zone(
        zone_id
    )