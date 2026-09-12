from fastapi import APIRouter

from database.zones_repository import get_all_zones


router = APIRouter(
    prefix="/zones",
    tags=["Zones"],
)


def clean_nan(value):
    """
    Convert NaN and Infinity values to None
    so the response is valid JSON.
    """

    if isinstance(value, float):

        # NaN
        if value != value:
            return None

        # +Infinity
        if value == float("inf"):
            return None

        # -Infinity
        if value == float("-inf"):
            return None

    if isinstance(value, dict):
        return {
            key: clean_nan(val)
            for key, val in value.items()
        }

    if isinstance(value, list):
        return [
            clean_nan(item)
            for item in value
        ]

    return value


@router.get("")
def get_zones():

    zones = get_all_zones()

    return [
        clean_nan(
            {
                "zone_id": zone["zone_id"],
                "name": zone["name"],
                "name_ar": zone.get("name_ar"),
                "name_local": zone.get("name_local"),
                "country": zone["country"],
                "country_code": zone.get("country_code"),
                "admin_level": zone.get("admin_level"),
                "region": zone.get("region"),
                "subregion": zone.get("subregion"),
                "coordinates": zone.get("coordinates"),
            }
        )
        for zone in zones
    ]
