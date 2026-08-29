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


USGS_URL = (
    "https://earthquake.usgs.gov/"
    "fdsnws/event/1/query"
)



# ============================================================
# AFRICA COUNTRY LOCATIONS
# Representative points for MVP coverage
#
# Future upgrade:
# country -> zones -> multiple coordinates
# ============================================================


COUNTRY_LOCATIONS = {


    # =========================
    # North Africa
    # =========================

    "Egypt": {
        "latitude": 26.8206,
        "longitude": 30.8025,
        "radius_km": 500,
    },


    "Morocco": {
        "latitude": 31.7917,
        "longitude": -7.0926,
        "radius_km": 500,
    },


    "Algeria": {
        "latitude": 28.0339,
        "longitude": 1.6596,
        "radius_km": 500,
    },



    # =========================
    # East Africa
    # =========================

    "Kenya": {
        "latitude": -0.0236,
        "longitude": 37.9062,
        "radius_km": 500,
    },


    "Ethiopia": {
        "latitude": 9.1450,
        "longitude": 40.4897,
        "radius_km": 500,
    },


    "Tanzania": {
        "latitude": -6.3690,
        "longitude": 34.8888,
        "radius_km": 500,
    },


    "Uganda": {
        "latitude": 1.3733,
        "longitude": 32.2903,
        "radius_km": 500,
    },



    # =========================
    # Nile / Horn Region
    # =========================

    "Sudan": {
        "latitude": 12.8628,
        "longitude": 30.2176,
        "radius_km": 500,
    },



    # =========================
    # West Africa
    # =========================

    "Nigeria": {
        "latitude": 9.0820,
        "longitude": 8.6753,
        "radius_km": 500,
    },


    "Ghana": {
        "latitude": 7.9465,
        "longitude": -1.0232,
        "radius_km": 500,
    },



    # =========================
    # Southern Africa
    # =========================

    "South Africa": {
        "latitude": -30.5595,
        "longitude": 22.9375,
        "radius_km": 500,
    },


    "Mozambique": {
        "latitude": -18.6657,
        "longitude": 35.5296,
        "radius_km": 500,
    },

}



# ============================================================
# FETCH EARTHQUAKES
# ============================================================


def get_earthquakes(
    country,
    start_time,
    end_time,
    min_magnitude=0,
):
    """
    Fetch earthquakes from USGS API.

    Returns:
        Raw GeoJSON response.
    """


    if country not in COUNTRY_LOCATIONS:

        raise ValueError(
            f"Country '{country}' is not configured."
        )


    location = COUNTRY_LOCATIONS[country]


    params = {

        "format":
            "geojson",

        "starttime":
            start_time,

        "endtime":
            end_time,

        "minmagnitude":
            min_magnitude,

        "latitude":
            location["latitude"],

        "longitude":
            location["longitude"],

        "maxradiuskm":
            location["radius_km"],

        "orderby":
            "time-desc",
    }



    try:

        response = requests.get(
            USGS_URL,
            params=params,
            timeout=30,
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
    data,
):
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

                "magnitude":
                    float(magnitude),


                "place":
                    properties.get(
                        "place"
                    ),


                "time":
                    properties.get(
                        "time"
                    ),


                "longitude":
                    coordinates[0],


                "latitude":
                    coordinates[1],


                "depth":
                    coordinates[2],

            }

        )


    return earthquakes



# ============================================================
# TIME CONVERSION
# ============================================================


def convert_timestamp(
    timestamp,
):
    """
    Convert USGS milliseconds timestamp.
    """


    return datetime.fromtimestamp(

        timestamp / 1000,

        tz=timezone.utc

    )



# ============================================================
# FEATURE EXTRACTION
# ============================================================


def extract_earthquake_features(
    earthquakes,
    recent_days=7,
):
    """
    Extract earthquake features required
    by MONJED scoring engine.
    """


    if not earthquakes:

        return {

            "earthquake_count":
                0,

            "max_magnitude":
                0.0,

            "average_magnitude":
                0.0,

            "recent_activity":
                0,

            "average_depth":
                0.0,
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


        "earthquake_count":
            count,


        "max_magnitude":
            round(
                max(magnitudes),
                2
            ),


        "average_magnitude":
            round(
                sum(magnitudes) / count,
                2
            ),


        "recent_activity":
            recent_activity,


        "average_depth":
            round(
                sum(depths) / len(depths),
                2
            )
            if depths
            else 0.0,

    }