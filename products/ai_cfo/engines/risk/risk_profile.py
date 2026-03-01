class RiskProfile:

    def __init__(
        self,
        liquidity_low_threshold,
        liquidity_high_threshold,
        burn_high_threshold,
        debt_high_threshold,
    ):
        self.liquidity_low_threshold = liquidity_low_threshold
        self.liquidity_high_threshold = liquidity_high_threshold
        self.burn_high_threshold = burn_high_threshold
        self.debt_high_threshold = debt_high_threshold

class SMERiskProfile:

    # =========================
    # Liquidity (Runway months)
    # =========================
    runway_high_risk = 4
    runway_medium_risk = 9

    # =========================
    # Burn Ratio
    # =========================
    burn_high_risk = 1.0
    burn_medium_risk = 0.6

    # =========================
    # Debt Ratio
    # =========================
    debt_high_risk = 0.7
    debt_medium_risk = 0.4

    # =========================
    # Revenue Volatility
    # =========================
    revenue_vol_high = 0.35
    revenue_vol_medium = 0.15