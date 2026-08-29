from app.schemas.flood import (
    FloodRiskInput,
    FloodRiskResult,
    RiskLevel,
    RainfallTrend,
)


def calculate_flood_risk(data: FloodRiskInput) -> FloodRiskResult:
    score = 0.0
    reasons = []

    # 1. Rainfall contribution — maximum 50 points
    if data.rainfall_mm >= 100:
        score += 50
        reasons.append("Very heavy recent rainfall")

    elif data.rainfall_mm >= 50:
        score += 35
        reasons.append("Heavy recent rainfall")

    elif data.rainfall_mm >= 20:
        score += 20
        reasons.append("Moderate recent rainfall")

    # 2. Soil moisture contribution — maximum 40 points
    if data.soil_moisture >= 0.8:
        score += 40
        reasons.append("Very high soil saturation")

    elif data.soil_moisture >= 0.6:
        score += 30
        reasons.append("High soil saturation")

    elif data.soil_moisture >= 0.4:
        score += 15
        reasons.append("Moderate soil saturation")

    # 3. Rainfall trend contribution — maximum 10 points
    if data.rainfall_trend == RainfallTrend.increasing:
        score += 10
        reasons.append("Rainfall trend is increasing")

    elif data.rainfall_trend == RainfallTrend.stable:
        score += 5
        reasons.append("Rainfall trend is stable")

    # Keep score between 0 and 100
    score = min(round(score, 1), 100)

    # 4. Convert score to risk level
    if score < 25:
        risk_level = RiskLevel.low

    elif score < 50:
        risk_level = RiskLevel.moderate

    elif score < 75:
        risk_level = RiskLevel.high

    else:
        risk_level = RiskLevel.critical

    if not reasons:
        reasons.append("No strong flood risk signals detected")

    return FloodRiskResult(
        risk_score=score,
        risk_level=risk_level,
        reasons=reasons,
    )