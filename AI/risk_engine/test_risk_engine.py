"""
MONJED AI - Risk Engine Integration Test

Tests:

NASA POWER
      |
      ↓
Flood Risk Engine


USGS
      |
      ↓
Earthquake Risk Engine


This test does NOT:
- generate alerts
- call Gemini
- send SMS
"""



import json



from AI.risk_engine.engine import (
    evaluate_flood_risk,
    evaluate_earthquake_risk,
)




# ============================================================
# HELPERS
# ============================================================


def print_result(
    title,
    data,
):

    print(
        f"\n========== {title} =========="
    )


    print(

        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    )




# ============================================================
# FLOOD TEST
# ============================================================


def test_flood():

    result = evaluate_flood_risk(
        country="Kenya",
        days_window=30,
    )


    print_result(
        "NASA POWER FLOOD RISK",
        result,
    )



# ============================================================
# EARTHQUAKE TEST
# ============================================================


def test_earthquake():

    result = evaluate_earthquake_risk(

        country="Kenya",

        days_window=30,

    )


    print_result(

        "USGS EARTHQUAKE RISK",

        result,

    )





# ============================================================
# RUN
# ============================================================


if __name__ == "__main__":


    print(
        """
=====================================
MONJED AI RISK ENGINE TEST
=====================================
"""
    )


    test_flood()


    test_earthquake()


    print(
        """
=====================================
TEST COMPLETED
=====================================
"""
    )