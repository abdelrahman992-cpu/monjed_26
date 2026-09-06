from fastapi import APIRouter, HTTPException

from database.zones_repository import get_all_zones


router = APIRouter(
    prefix="/zones",
    tags=["Zones"],
)


@router.get("")
def get_zones():

    zones = get_all_zones()

    return [
        {
            "zone_id": zone["zone_id"],
            "name": zone["name"],
            "country": zone["country"],
            "country_code": zone.get("country_code"),
            "region": zone.get("region"),
            "subregion": zone.get("subregion"),
            "coordinates": zone.get("coordinates"),
        }
        for zone in zones
    ]
