from app.schemas.risk import FloodRiskInput, RiskLevel


def calculate_confidence(data: FloodRiskInput) -> float:
    confidence = 0.65

    # حداثة البيانات
    if data.data_age_minutes <= 60:
        confidence += 0.15

    elif data.data_age_minutes <= 180:
        confidence += 0.05

    elif data.data_age_minutes > 360:
        confidence -= 0.15

    # وجود بيانات اليوم السابق
    if data.previous_rainfall_24h_mm is not None:
        confidence += 0.10

    confidence = max(
        0.0,
        min(confidence, 0.95),
    )

    return round(confidence, 2)


def calculate_flood_risk(
    data: FloodRiskInput,
) -> tuple[int, RiskLevel, list[str], float]:

    score = 0
    reasons = []

    # ========================================================
    # 1. CURRENT DAILY RAINFALL
    # ========================================================

    if data.rainfall_24h_mm >= 80:
        score += 60
        reasons.append(
            "High accumulated daily rainfall"
        )

    elif data.rainfall_24h_mm >= 40:
        score += 35
        reasons.append(
            "Elevated accumulated daily rainfall"
        )

    elif data.rainfall_24h_mm >= 20:
        score += 15
        reasons.append(
            "Moderate accumulated daily rainfall"
        )

    # ========================================================
    # 2. RAINFALL TREND
    # ========================================================

    if data.previous_rainfall_24h_mm is not None:

        increase = (
            data.rainfall_24h_mm
            - data.previous_rainfall_24h_mm
        )

        if increase >= 20:
            score += 40
            reasons.append(
                "Daily rainfall is increasing significantly"
            )

        elif increase >= 10:
            score += 20
            reasons.append(
                "Daily rainfall is increasing"
            )

    # ========================================================
    # 3. LIMIT SCORE
    # ========================================================

    score = max(
        0,
        min(score, 100),
    )

    # ========================================================
    # 4. RISK LEVEL
    # ========================================================

    if score >= 80:
        level: RiskLevel = "critical"

    elif score >= 60:
        level = "high"

    elif score >= 30:
        level = "moderate"

    else:
        level = "low"

    # ========================================================
    # 5. DEFAULT REASON
    # ========================================================

    if not reasons:
        reasons.append(
            "No significant rainfall-based "
            "flood-risk indicators detected"
        )

    # ========================================================
    # 6. CONFIDENCE
    # ========================================================

    confidence = calculate_confidence(data)

    return (
        score,
        level,
        reasons,
        confidence,
    )
