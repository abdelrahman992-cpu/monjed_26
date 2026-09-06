"""
MONJED AI - Earthquake Data Engine

Responsibilities:
- Fetch earthquake data from USGS
- Parse raw GeoJSON response
- Extract earthquake risk features

This module does NOT:
- calculate risk score
- generate decisions
- generate alerts
"""

import requests

from datetime import (
    datetime,
    timedelta,
    timezone,
)


# ============================================================
# CONFIGURATION
# ============================================================

USGS_URL = (
    "https://earthquake.usgs.gov/"
    "fdsnws/event/1/query"
)

REQUEST_TIMEOUT = 30


# ============================================================
# FETCH EARTHQUAKES
# ============================================================

def get_earthquakes(
    latitude: float,
    longitude: float,
    start_time: str,
    end_time: str,
    radius_km: float = 500,
    min_magnitude: float = 0,
) -> dict:
    """
    Fetch earthquakes from USGS API.

    Coordinates are provided dynamically
    by the MONJED zone/location.

    Returns:
        Raw GeoJSON response.
    """

    params = {
        "format": "geojson",
        "starttime": start_time,
        "endtime": end_time,
        "minmagnitude": min_magnitude,
        "latitude": latitude,
        "longitude": longitude,
        "maxradiuskm": radius_km,
        "orderby": "time-desc",
    }

    try:

        response = requests.get(
            USGS_URL,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException:

        # Fail safely.
        # MONJED should continue with empty evidence.

        return {
            "features": []
        }


# ============================================================
# PARSE RESPONSE
# ============================================================

def parse_earthquakes(
    data: dict,
) -> list:
    """
    Convert USGS GeoJSON into clean objects.
    """

    earthquakes = []

    for feature in data.get(
        "features",
        [],
    ):

        properties = feature.get(
            "properties",
            {},
        )

        geometry = feature.get(
            "geometry",
            {},
        )

        coordinates = geometry.get(
            "coordinates",
            [],
        )

        if len(coordinates) < 3:
            continue

        magnitude = properties.get(
            "mag"
        )

        if magnitude is None:
            continue

        earthquakes.append(
            {
                "magnitude": float(magnitude),

                "place": properties.get(
                    "place"
                ),

                "time": properties.get(
                    "time"
                ),

                "longitude": coordinates[0],

                "latitude": coordinates[1],

                "depth": coordinates[2],
            }
        )

    return earthquakes


# ============================================================
# TIME CONVERSION
# ============================================================

def convert_timestamp(
    timestamp: int,
) -> datetime:
    """
    Convert USGS milliseconds timestamp.
    """

    return datetime.fromtimestamp(
        timestamp / 1000,
        tz=timezone.utc,
    )


# ============================================================
# FEATURE EXTRACTION
# ============================================================

def extract_earthquake_features(
    earthquakes: list,
    recent_days: int = 7,
) -> dict:
    """
    Extract earthquake features required
    by MONJED scoring engine.
    """

    if not earthquakes:

        return {
            "earthquake_count": 0,
            "max_magnitude": 0.0,
            "average_magnitude": 0.0,
            "recent_activity": 0,
            "average_depth": 0.0,
        }

    magnitudes = [
        item["magnitude"]
        for item in earthquakes
    ]

    depths = [
        item["depth"]
        for item in earthquakes
        if item.get("depth") is not None
    ]

    count = len(
        magnitudes
    )

    cutoff = (
        datetime.now(
            timezone.utc
        )
        -
        timedelta(
            days=recent_days
        )
    )

    recent_activity = 0

    for earthquake in earthquakes:

        timestamp = earthquake.get(
            "time"
        )

        if timestamp is None:
            continue

        earthquake_time = convert_timestamp(
            timestamp
        )

        if earthquake_time >= cutoff:
            recent_activity += 1

    return {
        "earthquake_count": count,

        "max_magnitude": round(
            max(magnitudes),
            2,
        ),

        "average_magnitude": round(
            sum(magnitudes) / count,
            2,
        ),

        "recent_activity": recent_activity,

        "average_depth": round(
            sum(depths) / len(depths),
            2,
        )
        if depths
        else 0.0,
    }
