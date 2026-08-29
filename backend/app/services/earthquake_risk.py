from app.schemas.risk import (
    EarthquakeRiskInput,
    RiskLevel,
)


def calculate_earthquake_confidence(
    data: EarthquakeRiskInput
) -> float:

    confidence = 0.65

    # Trusted source such as USGS
    if data.source_verified:
        confidence += 0.15

    # Freshness
    if data.data_age_minutes <= 10:
        confidence += 0.15

    elif data.data_age_minutes <= 60:
        confidence += 0.10

    elif data.data_age_minutes <= 180:
        confidence += 0.05

    elif data.data_age_minutes > 360:
        confidence -= 0.10

    confidence = max(
        0.0,
        min(confidence, 0.95)
    )

    return round(confidence, 2)


def calculate_earthquake_risk(
    data: EarthquakeRiskInput
) -> tuple[int, RiskLevel, list[str], float]:

    score = 0
    reasons: list[str] = []

    # -------------------------
    # 1. Magnitude
    # -------------------------

    if data.magnitude >= 7:
        score += 60
        reasons.append(
            "Very strong earthquake magnitude"
        )

    elif data.magnitude >= 6:
        score += 45
        reasons.append(
            "Strong earthquake magnitude"
        )

    elif data.magnitude >= 5:
        score += 30
        reasons.append(
            "Moderate earthquake magnitude"
        )

    elif data.magnitude >= 4:
        score += 15
        reasons.append(
            "Light earthquake magnitude"
        )

    else:
        score += 5
        reasons.append(
            "Low earthquake magnitude"
        )

    # -------------------------
    # 2. Distance
    # -------------------------

    if data.distance_km <= 20:
        score += 25
        reasons.append(
            "Earthquake is very close to the affected zone"
        )

    elif data.distance_km <= 50:
        score += 18
        reasons.append(
            "Earthquake is close to the affected zone"
        )

    elif data.distance_km <= 100:
        score += 10
        reasons.append(
            "Earthquake is within regional proximity"
        )

    elif data.distance_km <= 200:
        score += 5

    # -------------------------
    # 3. Depth
    # -------------------------

    if data.depth_km <= 10:
        score += 15
        reasons.append(
            "Very shallow earthquake depth"
        )

    elif data.depth_km <= 30:
        score += 10
        reasons.append(
            "Shallow earthquake depth"
        )

    elif data.depth_km <= 70:
        score += 5

    # Never exceed 100
    score = min(score, 100)

    # -------------------------
    # Risk level
    # -------------------------

    if score >= 75:
        level: RiskLevel = "critical"

    elif score >= 50:
        level = "high"

    elif score >= 25:
        level = "moderate"

    else:
        level = "low"

    confidence = calculate_earthquake_confidence(data)

    return score, level, reasons, confidence