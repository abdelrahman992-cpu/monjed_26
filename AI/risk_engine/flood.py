"""
MONJED AI - Flood Data Engine

Responsibilities:
- Fetch rainfall data from NASA POWER
- Parse precipitation records
- Extract flood risk features
- Report data availability status


This module does NOT:
- calculate risk score
- make decisions
- generate alerts
"""


import requests



# ============================================================
# CONFIGURATION
# ============================================================


NASA_POWER_URL = (
    "https://power.larc.nasa.gov/"
    "api/temporal/daily/point"
)


REQUEST_TIMEOUT = 30


MAX_RETRIES = 2



# ============================================================
# AFRICA COUNTRY LOCATIONS
# Representative MVP coordinates
#
# Future:
# country -> zones -> multiple points
# ============================================================


COUNTRY_LOCATIONS = {

    "Egypt": {
        "latitude": 26.8206,
        "longitude": 30.8025,
    },

    "Morocco": {
        "latitude": 31.7917,
        "longitude": -7.0926,
    },

    "Algeria": {
        "latitude": 28.0339,
        "longitude": 1.6596,
    },


    "Kenya": {
        "latitude": -0.0236,
        "longitude": 37.9062,
    },


    "Ethiopia": {
        "latitude": 9.1450,
        "longitude": 40.4897,
    },


    "Tanzania": {
        "latitude": -6.3690,
        "longitude": 34.8888,
    },


    "Uganda": {
        "latitude": 1.3733,
        "longitude": 32.2903,
    },


    "Sudan": {
        "latitude": 12.8628,
        "longitude": 30.2176,
    },


    "Nigeria": {
        "latitude": 9.0820,
        "longitude": 8.6753,
    },


    "Ghana": {
        "latitude": 7.9465,
        "longitude": -1.0232,
    },


    "South Africa": {
        "latitude": -30.5595,
        "longitude": 22.9375,
    },


    "Mozambique": {
        "latitude": -18.6657,
        "longitude": 35.5296,
    },

}



# ============================================================
# FETCH NASA DATA
# ============================================================


def get_rainfall_data(
    country: str,
    start_date: str,
    end_date: str,
) -> dict:
    """
    Fetch rainfall data from NASA POWER.

    Returns:

    {
        "available": True,
        "source": "NASA_POWER",
        "data": {...}
    }


    If unavailable:

    {
        "available": False,
        "source": "NASA_POWER",
        "error": "..."
    }

    """


    if country not in COUNTRY_LOCATIONS:

        raise ValueError(
            f"Country '{country}' is not configured."
        )



    location = COUNTRY_LOCATIONS[country]



    params = {

        "parameters":
            "PRECTOTCORR",


        "community":
            "RE",


        "longitude":
            location["longitude"],


        "latitude":
            location["latitude"],


        "start":
            start_date.replace(
                "-",
                ""
            ),


        "end":
            end_date.replace(
                "-",
                ""
            ),


        "format":
            "JSON",

    }



    last_error = None



    for _ in range(
        MAX_RETRIES + 1
    ):


        try:

            response = requests.get(

                NASA_POWER_URL,

                params=params,

                timeout=REQUEST_TIMEOUT,

            )


            response.raise_for_status()



            data = response.json()



            return {

                "available":
                    True,


                "source":
                    "NASA_POWER",


                "data":
                    data,

            }



        except Exception as error:

            last_error = str(error)



    return {

        "available":
            False,


        "source":
            "NASA_POWER",


        "error":
            last_error,

        "data":
            {},

    }



# ============================================================
# PARSE DATA
# ============================================================


def parse_rainfall_data(
    raw_data: dict,
) -> dict:
    """
    Extract clean rainfall values.

    Returns empty data only when
    no valid rainfall records exist.
    """


    if not isinstance(
        raw_data,
        dict,
    ):

        return {}



    payload = raw_data.get(
        "data",
        raw_data,
    )



    try:

        parameters = (
            payload
            .get(
                "properties",
                {}
            )
            .get(
                "parameter",
                {}
            )
        )


        rainfall = parameters.get(
            "PRECTOTCORR",
            {}
        )



        return {

            date: value

            for date, value in rainfall.items()

            if isinstance(
                value,
                (int, float),
            )

            and value >= 0

        }



    except Exception:

        return {}



# ============================================================
# FEATURE EXTRACTION
# ============================================================


def extract_flood_features(
    rainfall_data: dict,
    recent_days: int = 3,
) -> dict:
    """
    Extract flood-related rainfall features.

    Does NOT calculate risk.
    """


    if not rainfall_data:


        return {

            "average_daily_rainfall":
                0.0,


            "recent_daily_rainfall":
                0.0,


            "cumulative_rainfall":
                0.0,


            "days_analyzed":
                0,


            "data_available":
                False,

        }



    dates = sorted(
        rainfall_data.keys()
    )


    values = [

        rainfall_data[d]

        for d in dates

    ]



    total = sum(
        values
    )


    days = len(
        values
    )



    recent_values = values[
        -recent_days:
    ]



    return {


        "average_daily_rainfall":
            round(
                total / days,
                2
            ),



        "recent_daily_rainfall":
            round(
                sum(recent_values)
                /
                len(recent_values),
                2
            ),



        "cumulative_rainfall":
            round(
                total,
                2
            ),



        "days_analyzed":
            days,


        "data_available":
            True,

    }