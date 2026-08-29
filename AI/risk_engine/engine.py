"""
MONJED AI Risk Engine Orchestrator

Responsible for:
- Collecting hazard data
- Extracting features
- Running scoring models
- Returning standardized risk assessment


Does NOT:
- make decisions
- generate alerts
- communicate with users
"""


from datetime import (
    datetime,
    timedelta,
    timezone,
)



from .earthquake import (
    get_earthquakes,
    parse_earthquakes,
    extract_earthquake_features,
)



from .flood import (
    get_rainfall_data,
    parse_rainfall_data,
    extract_flood_features,
)



from .scoring import (
    calculate_earthquake_score,
    calculate_flood_score,
)



# ============================================================
# HELPERS
# ============================================================


def _current_time():

    return datetime.now(
        timezone.utc
    )



# ============================================================
# EARTHQUAKE
# ============================================================


def evaluate_earthquake_risk(
    country: str,
    days_window: int = 30,
):


    now = _current_time()


    start = now - timedelta(
        days=days_window
    )



    raw_data = get_earthquakes(

        country=country,

        start_time=start.strftime(
            "%Y-%m-%d"
        ),

        end_time=now.strftime(
            "%Y-%m-%d"
        ),

        min_magnitude=2.0,

    )



    try:

        cleaned = parse_earthquakes(
            raw_data
        )


        features = extract_earthquake_features(
            cleaned,
            recent_days=7,
        )


        assessment = calculate_earthquake_score(
            features
        )


    except Exception as error:


        return {

            "hazard":
                "earthquake",

            "country":
                country,

            "risk_score":
                0,

            "risk_level":
                "unknown",

            "confidence":
                0,

            "reasons":
                [
                    f"Earthquake data processing failed: {error}"
                ],

            "features":
                {},

            "data_available":
                False,

            "evaluated_at":
                now.isoformat(),

        }



    return {

        "hazard":
            "earthquake",


        "country":
            country,


        "risk_score":
            assessment["score"],


        "risk_level":
            assessment["risk_level"],


        "confidence":
            assessment["confidence"],


        "reasons":
            assessment["reasons"],


        "features":
            features,


        "data_available":
            True,


        "data_source":
            "USGS",


        "evaluated_at":
            now.isoformat(),

    }




# ============================================================
# FLOOD
# ============================================================


def evaluate_flood_risk(
    country: str,
    days_window: int = 30,
):


    now = _current_time()



    start = now - timedelta(
        days=days_window
    )



    raw_data = get_rainfall_data(

        country=country,

        start_date=start.strftime(
            "%Y-%m-%d"
        ),

        end_date=now.strftime(
            "%Y-%m-%d"
        ),

    )



    # NASA unavailable

    if not raw_data.get(
        "available",
        False,
    ):


        return {

            "hazard":
                "flood",


            "country":
                country,


            "risk_score":
                0,


            "risk_level":
                "unknown",


            "confidence":
                0,


            "reasons":

                [
                    "NASA POWER rainfall data unavailable."
                ],


            "features":
                {},


            "data_available":
                False,


            "data_source":
                "NASA_POWER",


            "evaluated_at":
                now.isoformat(),

        }



    cleaned = parse_rainfall_data(
        raw_data
    )



    features = extract_flood_features(

        cleaned,

        recent_days=3,

    )



    assessment = calculate_flood_score(
        features
    )



    return {


        "hazard":

            "flood",



        "country":

            country,



        "risk_score":

            assessment["score"],



        "risk_level":

            assessment["risk_level"],



        "confidence":

            assessment["confidence"],



        "reasons":

            assessment["reasons"],



        "features":

            features,



        "data_available":

            True,



        "data_source":

            "NASA_POWER",



        "evaluated_at":

            now.isoformat(),

    }