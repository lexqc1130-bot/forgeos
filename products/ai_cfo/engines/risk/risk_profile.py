class RiskProfile:

    def __init__(
        self,
        liquidity_low_threshold,
        liquidity_high_threshold,
        burn_high_threshold,
        debt_high_threshold,
        stage="stable",
        base_risk_weight=2.0,
        base_cost_weight=1.5
    ):
        # ---- Risk thresholds ----
        self.liquidity_low_threshold = liquidity_low_threshold
        self.liquidity_high_threshold = liquidity_high_threshold
        self.burn_high_threshold = burn_high_threshold
        self.debt_high_threshold = debt_high_threshold

        # ---- Strategy personality ----
        self.stage = stage
        self.base_risk_weight = base_risk_weight
        self.base_cost_weight = base_cost_weight

    # 🔥 Decision Preference Vector
    def decision_weights(self, risk_level, fragility):

        risk_weight = self.base_risk_weight
        cost_weight = self.base_cost_weight

        # -------------------------
        # Stage influence
        # -------------------------
        if self.stage == "growth":
            risk_weight += 1.5
            cost_weight -= 0.5

        elif self.stage == "distressed":
            risk_weight += 3.0
            cost_weight -= 1.0

        # -------------------------
        # Risk level influence
        # -------------------------
        if risk_level == "HIGH":
            risk_weight += 2.0
            cost_weight -= 0.5

        # -------------------------
        # Fragility influence
        # -------------------------
        if fragility >= 1.4:
            risk_weight += 1.0

        # 保護 cost_weight 不為負
        cost_weight = max(cost_weight, 0.1)

        return risk_weight, cost_weight


class SMERiskProfile:

    def __init__(self, stage="stable"):
        self.stage = stage

        # =========================
        # Liquidity (Runway months)
        # =========================
        self.runway_high_risk = 4
        self.runway_medium_risk = 9

        # =========================
        # Burn Ratio
        # =========================
        self.burn_high_risk = 1.0
        self.burn_medium_risk = 0.6

        # =========================
        # Debt Ratio
        # =========================
        self.debt_high_risk = 0.7
        self.debt_medium_risk = 0.4

        # =========================
        # Revenue Volatility
        # =========================
        self.revenue_vol_high = 0.35
        self.revenue_vol_medium = 0.15

        # ---- Strategy defaults ----
        self.base_risk_weight = 2.0
        self.base_cost_weight = 1.5

    # 🔥 Decision Preference Vector
    def decision_weights(self, risk_level, fragility):

        risk_weight = self.base_risk_weight
        cost_weight = self.base_cost_weight

        # Stage influence
        if self.stage == "growth":
            risk_weight += 1.5
            cost_weight -= 0.5

        elif self.stage == "distressed":
            risk_weight += 3.0
            cost_weight -= 1.0

        # Risk level influence
        if risk_level == "HIGH":
            risk_weight += 2.0
            cost_weight -= 0.5

        # Fragility influence
        if fragility >= 1.4:
            risk_weight += 1.0

        cost_weight = max(cost_weight, 0.1)

        return risk_weight, cost_weight