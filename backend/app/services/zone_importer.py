"""
MONJED Global Zone Importer

Imports global administrative level-1 regions
(states, provinces, governorates, etc.)
from Natural Earth into MongoDB.

Source:
Natural Earth Admin-1 States/Provinces
"""

from datetime import datetime, timezone
import math

import geopandas as gpd

from database.connection import get_database


NATURAL_EARTH_URL = (
    "https://naturalearth.s3.amazonaws.com/"
    "10m_cultural/"
    "ne_10m_admin_1_states_provinces.zip"
)


def get_zones_collection():
    return get_database()["zones"]


def clean_value(value):
    """
    Convert NaN values to None so they can be stored
    and returned as valid JSON.
    """

    if value is None:
        return None

    if isinstance(value, float) and math.isnan(value):
        return None

    return value


def import_zones():
    print("Downloading Natural Earth Admin-1 data...")

    gdf = gpd.read_file(NATURAL_EARTH_URL)

    print(
        f"Loaded {len(gdf)} administrative regions."
    )

    collection = get_zones_collection()

    now = datetime.now(timezone.utc)

    imported = 0
    skipped = 0

    for _, row in gdf.iterrows():

        country_code = clean_value(
            row.get("iso_a2")
        )

        zone_name = (
            row.get("name_en")
            or row.get("name")
        )

        zone_name = clean_value(zone_name)

        if (
            not country_code
            or country_code == "-99"
        ):
            skipped += 1
            continue

        if not zone_name:
            skipped += 1
            continue

        latitude = row.get("latitude")
        longitude = row.get("longitude")

        if (
            latitude is None
            or longitude is None
        ):
            skipped += 1
            continue

        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (TypeError, ValueError):
            skipped += 1
            continue

        if (
            not math.isfinite(latitude)
            or not math.isfinite(longitude)
        ):
            skipped += 1
            continue

        adm1_code = clean_value(
            row.get("adm1_code")
        )

        if not adm1_code:
            skipped += 1
            continue

        zone_id = (
            f"{country_code}-{adm1_code}"
        )

        zone = {
            "zone_id": zone_id,
            "name": zone_name,
            "name_local": clean_value(
                row.get("name_local")
            ),
            "name_ar": clean_value(
                row.get("name_ar")
            ),
            "country_code": country_code,
            "country": clean_value(
                row.get("admin")
            ),
            "region": clean_value(
                row.get("region")
            ),
            "subregion": clean_value(
                row.get("region_sub")
            ),
            "coordinates": [
                longitude,
                latitude,
            ],
            "admin_level": 1,
            "source": "Natural Earth",
            "source_version": "10m",
            "created_at": now,
            "updated_at": now,
        }

        collection.update_one(
            {
                "zone_id": zone_id
            },
            {
                "$set": zone
            },
            upsert=True,
        )

        imported += 1

        if imported % 100 == 0:
            print(
                f"Imported: {imported}"
            )

    print()
    print("================================")
    print("ZONE IMPORT COMPLETED")
    print("================================")
    print(f"Imported: {imported}")
    print(f"Skipped:  {skipped}")
    print("MongoDB:  monjed.zones")


if __name__ == "__main__":
    import_zones()
