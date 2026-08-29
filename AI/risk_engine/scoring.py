"""
MONJED AI Risk Scoring Engine

Responsible for:
- Feature normalization
- Hazard scoring
- Risk classification
- Explainable reasons
- Confidence estimation


This module does NOT:
- generate alerts
- make decisions
- communicate with users
"""


# ============================================================
# RISK LEVELS
# ============================================================


RISK_THRESHOLDS = {

    "moderate": 30,

    "high": 60,

    "critical": 80,

}



def get_risk_level(
    score: float,
) -> str:

    if score < RISK_THRESHOLDS["moderate"]:
        return "low"

    if score < RISK_THRESHOLDS["high"]:
        return "moderate"

    if score < RISK_THRESHOLDS["critical"]:
        return "high"

    return "critical"



# ============================================================
# CONFIDENCE
# ============================================================


def calculate_confidence(
    data_available=True,
    days_analyzed=None,
):
    """
    Estimate confidence based on
    data quality.
    """


    if not data_available:

        return 0.0



    if days_analyzed is None:

        return 0.7



    if days_analyzed >= 14:

        return 0.95



    if days_analyzed >= 7:

        return 0.85



    return 0.7




# ============================================================
# NORMALIZATION
# ============================================================


def normalize(
    value,
    min_val,
    max_val,
):

    try:

        value = float(value)

    except:

        return 0.0



    if value <= min_val:

        return 0.0



    if value >= max_val:

        return 100.0



    return (
        (value - min_val)
        /
        (max_val - min_val)
    ) * 100



# ============================================================
# EARTHQUAKE
# ============================================================


EARTHQUAKE_WEIGHTS = {

    "count": 0.25,

    "max_magnitude": 0.35,

    "average_magnitude": 0.20,

    "recent_activity": 0.20,

}



def calculate_earthquake_score(
    features: dict,
):


    count = features.get(
        "earthquake_count",
        0,
    )


    max_mag = features.get(
        "max_magnitude",
        0,
    )


    avg_mag = features.get(
        "average_magnitude",
        0,
    )


    recent = features.get(
        "recent_activity",
        0,
    )



    count_score = normalize(
        count,
        0,
        10,
    )


    max_mag_score = normalize(
        max_mag,
        3,
        7,
    )


    avg_mag_score = normalize(
        avg_mag,
        3,
        6,
    )


    recent_score = normalize(
        recent,
        0,
        5,
    )



    score = round(

        (
            count_score
            *
            EARTHQUAKE_WEIGHTS["count"]
        )

        +

        (
            max_mag_score
            *
            EARTHQUAKE_WEIGHTS["max_magnitude"]
        )

        +

        (
            avg_mag_score
            *
            EARTHQUAKE_WEIGHTS["average_magnitude"]
        )

        +

        (
            recent_score
            *
            EARTHQUAKE_WEIGHTS["recent_activity"]
        ),

        2,

    )



    reasons = []



    if max_mag >= 6:

        reasons.append(
            f"Strong earthquake magnitude detected ({max_mag})."
        )


    elif max_mag >= 4.5:

        reasons.append(
            f"Moderate earthquake activity detected ({max_mag})."
        )



    if recent >= 3:

        reasons.append(
            f"Recent seismic activity increased ({recent} events)."
        )



    if count >= 8:

        reasons.append(
            f"High earthquake frequency detected ({count} events)."
        )



    if count == 0:

        reasons.append(
            "No significant earthquake activity detected."
        )



    return {

        "score": score,

        "risk_level":
            get_risk_level(score),

        "confidence":
            calculate_confidence(
                True
            ),

        "reasons":
            reasons,

        "sub_scores":
            {

                "count":
                    round(count_score,1),

                "max_magnitude":
                    round(max_mag_score,1),

                "average_magnitude":
                    round(avg_mag_score,1),

                "recent_activity":
                    round(recent_score,1),

            },

    }



# ============================================================
# FLOOD
# ============================================================


FLOOD_WEIGHTS = {

    "average_daily":0.25,

    "recent_daily":0.45,

    "cumulative":0.30,

}



def calculate_flood_score(
    features: dict,
):


    data_available = features.get(
        "data_available",
        True,
    )


    days = features.get(
        "days_analyzed",
        0,
    )


    if not data_available:

        return {

            "score":0,

            "risk_level":
                "unknown",

            "confidence":
                0.0,

            "reasons":
                [
                    "Rainfall data unavailable from NASA POWER."
                ],

            "sub_scores":
                {},

        }



    avg_daily = features.get(
        "average_daily_rainfall",
        0,
    )


    recent_daily = features.get(
        "recent_daily_rainfall",
        0,
    )


    cumulative = features.get(
        "cumulative_rainfall",
        0,
    )



    avg_score = normalize(
        avg_daily,
        0,
        25,
    )


    recent_score = normalize(
        recent_daily,
        0,
        50,
    )


    cumulative_score = normalize(
        cumulative,
        0,
        200,
    )



    score = round(

        (
            avg_score
            *
            FLOOD_WEIGHTS["average_daily"]
        )

        +

        (
            recent_score
            *
            FLOOD_WEIGHTS["recent_daily"]
        )

        +

        (
            cumulative_score
            *
            FLOOD_WEIGHTS["cumulative"]
        ),

        2,

    )



    reasons = []



    if recent_daily >= 30:

        reasons.append(
            f"Heavy recent rainfall ({recent_daily} mm/day)."
        )


    if cumulative >= 150:

        reasons.append(
            f"High accumulated rainfall ({cumulative} mm)."
        )


    if score < 10:

        reasons.append(
            "Low flood indicators detected."
        )



    return {

        "score":

            score,


        "risk_level":

            get_risk_level(score),


        "confidence":

            calculate_confidence(
                True,
                days,
            ),


        "reasons":

            reasons,


        "sub_scores":

            {

                "average_daily":
                    round(avg_score,1),

                "recent_daily":
                    round(recent_score,1),

                "cumulative":
                    round(cumulative_score,1),

            },

    }