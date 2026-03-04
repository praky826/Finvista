"""
Health Score Engine — Generates a 0-100 financial health score.
Weighted average of 5 normalized metrics, each worth 20%.
NO database access.
"""
from decimal import Decimal, ROUND_HALF_UP


def calculate_health_score(
    savings_ratio: Decimal,
    dti: Decimal,
    emergency_fund: Decimal,
    credit_utilization: Decimal,
    diversification_avg: Decimal,
) -> Decimal:
    """
    Health Score (0-100) — Weighted normalized score.

    Each metric normalized to 0-100, then weighted equally at 20%.

    Interpretation:
    - 80-100: Excellent
    - 60-80:  Good
    - 40-60:  Average
    - 20-40:  Poor
    - 0-20:   Critical
    """
    # Savings Ratio: Ideal ≥30% → score 100
    norm_savings = min((savings_ratio / 30) * 100, Decimal(100))

    # DTI: Ideal <30% → low DTI = high score; 40%+ = 0
    norm_dti = max(Decimal(100) - (dti * Decimal("2.5")), Decimal(0))
    norm_dti = min(norm_dti, Decimal(100))

    # Emergency Fund: Ideal ≥6 months → score 100
    norm_emergency = min((emergency_fund / 6) * 100, Decimal(100))

    # Credit Utilization: Ideal 0% → score 100; 100% → 0
    norm_credit = max(Decimal(100) - credit_utilization, Decimal(0))

    # Diversification: Ideal ≤25% concentration → 100
    if diversification_avg <= Decimal(25):
        norm_diversification = Decimal(100)
    elif diversification_avg <= Decimal(50):
        norm_diversification = max(Decimal(100) - ((diversification_avg - 25) * 2), Decimal(0))
    else:
        norm_diversification = Decimal(0)

    # Apply weights (20% each)
    health_score = (
        norm_savings * Decimal("0.20")
        + norm_dti * Decimal("0.20")
        + norm_emergency * Decimal("0.20")
        + norm_credit * Decimal("0.20")
        + norm_diversification * Decimal("0.20")
    )

    return health_score.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
