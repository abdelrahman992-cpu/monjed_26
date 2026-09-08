from app.schemas.risk import FloodRiskInput, RiskLevel


# ============================================================
# FLOOD EVIDENCE CONFIDENCE
# ============================================================

def calculate_confidence(
    data: FloodRiskInput,
) -> float:
    """
    Estimate confidence in the flood-risk assessment.

    IMPORTANT:
    - This is NOT the probability that a flood will happen.
    - It represents the quality, freshness, and completeness
      of the scientific evidence available to the Risk Engine.
    - Community reports do NOT affect this value.
    """

    confidence = 0.65

    # --------------------------------------------------------
    # 1. Data freshness
    # --------------------------------------------------------

    if data.data_age_minutes <= 60:
        confidence += 0.15

    elif data.data_age_minutes <= 180:
        confidence += 0.05

    elif data.data_age_minutes > 360:
        confidence -= 0.15

    # --------------------------------------------------------
    # 2. Trend evidence availability
    # --------------------------------------------------------

    if data.previous_rainfall_24h_mm is not None:
        confidence += 0.10

    # --------------------------------------------------------
    # Safe confidence bounds
    # --------------------------------------------------------

    confidence = max(
        0.0,
        min(confidence, 0.95),
    )

    return round(
        confidence,
        2,
    )


# ============================================================
# FLOOD RISK ENGINE
# ============================================================

def calculate_flood_risk(
    data: FloodRiskInput,
) -> tuple[int, RiskLevel, list[str], float]:
    """
    Calculate deterministic flood risk from rainfall evidence.

    The Risk Engine uses only scientific/environmental inputs.

    Community reports are intentionally excluded from:
    - risk_score
    - risk_level
    - confidence

    Community evidence is handled later by the
    Decision Engine as operational evidence.
    """

    score = 0
    reasons: list[str] = []

    # ========================================================
    # 1. Short-term rainfall
    #
    # Maximum contribution: 35 points
    # ========================================================

    if data.rainfall_1h_mm >= 30:
        score += 35

        reasons.append(
            "High short-term rainfall"
        )

    elif data.rainfall_1h_mm >= 15:
        score += 20

        reasons.append(
            "Elevated short-term rainfall"
        )

    # ========================================================
    # 2. Accumulated rainfall
    #
    # Maximum contribution: 45 points
    # ========================================================

    if data.rainfall_24h_mm >= 80:
        score += 45

        reasons.append(
            "High accumulated rainfall"
        )

    elif data.rainfall_24h_mm >= 40:
        score += 25

        reasons.append(
            "Elevated accumulated rainfall"
        )

    # ========================================================
    # 3. Rainfall trend
    #
    # Maximum contribution: 20 points
    # ========================================================

    if data.previous_rainfall_24h_mm is not None:

        increase = (
            data.rainfall_24h_mm
            - data.previous_rainfall_24h_mm
        )

        if increase >= 20:
            score += 20

            reasons.append(
                "Accumulated rainfall is increasing significantly"
            )

        elif increase >= 10:
            score += 10

            reasons.append(
                "Accumulated rainfall is increasing"
            )

    # ========================================================
    # Score safety
    # ========================================================

    score = max(
        0,
        min(score, 100),
    )

    # ========================================================
    # Risk classification
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
    # Confidence
    # ========================================================

    confidence = calculate_confidence(
        data
    )

    # ========================================================
    # Explanation fallback
    # ========================================================

    if not reasons:
        reasons.append(
            "No significant rainfall-based flood-risk indicators detected"
        )

    return (
        score,
        level,
        reasons,
        confidence,
    )