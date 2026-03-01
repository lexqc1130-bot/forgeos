class ScenarioSimulator:

    def __init__(self, risk_engine):
        self.risk_engine = risk_engine

    def simulate(
        self,
        snapshot,
        revenue_change=0.0,
        burn_change=0.0,
        debt_change=0.0,
        cash_shock=0.0,
        receivable_delay_months=0
    ):

        original = snapshot.copy()
        modified = snapshot.copy()

        # -------------------------
        # Revenue Change
        # -------------------------
        modified["monthly_revenue"] = snapshot.get("monthly_revenue", 0) * (1 + revenue_change)

        # -------------------------
        # Burn Change
        # -------------------------
        modified["monthly_burn"] = snapshot.get("monthly_burn", 0) * (1 + burn_change)

        # -------------------------
        # Debt Change
        # -------------------------
        modified["total_debt"] = snapshot.get("total_debt", 0) * (1 + debt_change)

        # -------------------------
        # Cash Shock (一次性現金變化)
        # -------------------------
        modified["cash"] = snapshot.get("cash", 0) + cash_shock

        # -------------------------
        # Receivable Delay Effect
        # 簡化模型：延遲回款 = 減少現金
        # 假設：每延遲1個月，等於減少一個月營收現金流
        # -------------------------
        if receivable_delay_months > 0:
            revenue = snapshot.get("monthly_revenue", 0)
            delay_impact = revenue * receivable_delay_months
            modified["cash"] -= delay_impact

        # 避免負數現金
        if modified["cash"] < 0:
            modified["cash"] = 0

        original_result = self.risk_engine.run(original)
        scenario_result = self.risk_engine.run(modified)

        return {
            "original": original_result,
            "scenario": scenario_result,
            "delta_score": (
                scenario_result["current"]["final_score"]
                - original_result["current"]["final_score"]
            )
        }