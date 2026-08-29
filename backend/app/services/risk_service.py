"""
MONJED AI - Risk Service Layer

Bridge between:

Backend
    |
    ↓
Risk Engine
    |
    ↓
Backend Assessment


Responsibilities:
- Call MONJED Risk Engine.
- Validate hazard requests.
- Normalize risk output.
- Provide stable interface for backend.


IMPORTANT:
- Does NOT calculate risk.
- Does NOT make decisions.
- Does NOT generate alerts.
- Risk Engine remains the source of truth.
"""


from datetime import datetime, timezone



from AI.risk_engine.engine import (
    evaluate_flood_risk,
    evaluate_earthquake_risk,
)



# ============================================================
# CONSTANTS
# ============================================================


SUPPORTED_HAZARDS = {

    "flood",

    "earthquake",

}



DEFAULT_LANGUAGE = "en"



# ============================================================
# HELPERS
# ============================================================


def _validate_hazard(
    hazard: str,
) -> str:
    """
    Validate requested hazard type.
    """


    if not isinstance(
        hazard,
        str,
    ):

        raise TypeError(
            "hazard must be a string."
        )



    normalized = (
        hazard
        .lower()
        .strip()
    )



    if normalized not in SUPPORTED_HAZARDS:

        raise ValueError(
            f"Unsupported hazard: {hazard}"
        )



    return normalized





def _validate_country(
    country: str,
) -> str:
    """
    Validate country input.
    """


    if not isinstance(
        country,
        str,
    ):

        raise TypeError(
            "country must be a string."
        )



    country = country.strip()



    if not country:

        raise ValueError(
            "country cannot be empty."
        )



    return country





def _normalize_risk_result(
    result: dict,
    language: str = DEFAULT_LANGUAGE,
) -> dict:
    """
    Convert Risk Engine output into
    MONJED backend assessment format.
    """


    if not isinstance(
        result,
        dict,
    ):

        raise TypeError(
            "Risk Engine returned invalid result."
        )



    return {


        "risk":

            {


                "hazard":

                    result.get(
                        "hazard",
                        "unknown",
                    ),



                "country":

                    result.get(
                        "country",
                        "unknown",
                    ),



                "risk_score":

                    result.get(
                        "risk_score",
                        0,
                    ),



                "risk_level":

                    result.get(
                        "risk_level",
                        "unknown",
                    ),



                "confidence":

                    result.get(
                        "confidence",
                        0,
                    ),



                "reasons":

                    result.get(
                        "reasons",
                        [],
                    ),



                "features":

                    result.get(
                        "features",
                        {},
                    ),



                "data_available":

                    result.get(
                        "data_available",
                        False,
                    ),



                "data_source":

                    result.get(
                        "data_source",
                        "unknown",
                    ),


            },



        "metadata":

            {


                "source":

                    "MONJED_RISK_ENGINE",



                "language":

                    language,



                "evaluated_at":

                    result.get(

                        "evaluated_at",

                        datetime.now(
                            timezone.utc
                        ).isoformat(),

                    ),

            },


    }





# ============================================================
# MAIN SERVICE
# ============================================================


def run_risk_assessment(
    hazard: str,
    country: str,
    language: str = DEFAULT_LANGUAGE,
    days_window: int = 30,
) -> dict:
    """
    Execute MONJED Risk Engine.

    Example:

        run_risk_assessment(
            "flood",
            "Kenya"
        )


    Returns:

    {
        risk:{},
        metadata:{}
    }

    """


    hazard = _validate_hazard(
        hazard
    )


    country = _validate_country(
        country
    )



    if not isinstance(
        days_window,
        int,
    ):

        raise TypeError(
            "days_window must be integer."
        )



    if days_window <= 0:

        raise ValueError(
            "days_window must be positive."
        )



    # --------------------------------------------------------
    # Execute Risk Engine
    # --------------------------------------------------------


    if hazard == "flood":


        result = evaluate_flood_risk(

            country,

            days_window,

        )



    elif hazard == "earthquake":


        result = evaluate_earthquake_risk(

            country,

            days_window,

        )



    else:

        raise ValueError(
            "Unsupported hazard."
        )



    return _normalize_risk_result(

        result,

        language,

    )