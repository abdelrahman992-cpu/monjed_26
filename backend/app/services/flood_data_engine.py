"""
MONJED AI - Flood Data Engine

مسؤول عن:
- جلب بيانات الأمطار من NASA POWER
- تحليل بيانات Daily Precipitation
- استخراج Features نستخدمها في حساب Flood Risk

لا يقوم هذا الملف بحساب Risk Score.
"""

from datetime import datetime, timedelta, timezone

import requests


NASA_POWER_URL = (
    "https://power.larc.nasa.gov/"
    "api/temporal/daily/point"
)

REQUEST_TIMEOUT = 30
MAX_RETRIES = 2


def get_rainfall_data(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
) -> dict:
    """
    جلب بيانات الأمطار اليومية من NASA POWER.

    start_date / end_date:
        YYYY-MM-DD

    مثال:
        get_rainfall_data(
            latitude=26.8206,
            longitude=30.8025,
            start_date="2026-09-01",
            end_date="2026-09-04",
        )
    """

    params = {
        "parameters": "PRECTOTCORR",
        "community": "RE",
        "longitude": longitude,
        "latitude": latitude,
        "start": start_date.replace("-", ""),
        "end": end_date.replace("-", ""),
        "format": "JSON",
        "time-standard": "UTC",
    }

    last_error = None

    for _ in range(MAX_RETRIES + 1):
        try:
            response = requests.get(
                NASA_POWER_URL,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            data = response.json()

            return {
                "available": True,
                "source": "NASA_POWER",
                "data": data,
            }

        except requests.RequestException as error:
            last_error = str(error)

        except ValueError as error:
            last_error = f"Invalid JSON response: {error}"

        except Exception as error:
            last_error = str(error)

    return {
        "available": False,
        "source": "NASA_POWER",
        "error": last_error,
        "data": {},
    }


def parse_rainfall_data(raw_data: dict) -> dict:
    """
    استخراج PRECTOTCORR من Response بتاع NASA POWER.

    الناتج:
        {
            "20260901": 2.31,
            "20260902": 0.00,
            "20260903": 15.42
        }
    """

    if not isinstance(raw_data, dict):
        return {}

    payload = raw_data.get("data", raw_data)

    try:
        parameters = (
            payload
            .get("properties", {})
            .get("parameter", {})
        )

        rainfall = parameters.get("PRECTOTCORR", {})

        return {
            date: float(value)
            for date, value in rainfall.items()
            if isinstance(value, (int, float))
            and value >= 0
        }

    except (AttributeError, TypeError, ValueError):
        return {}


def extract_flood_features(
    rainfall_data: dict,
) -> dict:
    """
    استخراج البيانات التي يحتاجها Flood Risk Engine.

    ملاحظة:
    NASA POWER Daily API يعطينا إجمالي المطر اليومي،
    وليس rolling 24-hour sensor measurement.
    """

    if not rainfall_data:
        return {
            "rainfall_24h_mm": 0.0,
            "previous_rainfall_24h_mm": None,
            "latest_observation_date": None,
            "data_age_minutes": None,
            "days_analyzed": 0,
            "data_available": False,
        }

    dates = sorted(rainfall_data.keys())

    latest_date = dates[-1]

    latest_value = float(
        rainfall_data[latest_date]
    )

    latest_dt = datetime.strptime(
        latest_date,
        "%Y%m%d",
    ).date()

    # اليوم السابق مباشرة
    previous_date = latest_dt - timedelta(days=1)

    previous_key = previous_date.strftime(
        "%Y%m%d"
    )

    previous_value = rainfall_data.get(
        previous_key
    )

    # نعتبر الـDaily record مكتملًا
    # عند بداية اليوم التالي UTC.
    observation_end = datetime.combine(
        latest_dt + timedelta(days=1),
        datetime.min.time(),
        tzinfo=timezone.utc,
    )

    age_minutes = max(
        0,
        int(
            (
                datetime.now(timezone.utc)
                - observation_end
            ).total_seconds()
            / 60
        ),
    )

    return {
        "rainfall_24h_mm": round(
            latest_value,
            2,
        ),

        "previous_rainfall_24h_mm": (
            round(float(previous_value), 2)
            if previous_value is not None
            else None
        ),

        "latest_observation_date": latest_date,

        "data_age_minutes": age_minutes,

        "days_analyzed": len(dates),

        "data_available": True,
    }
