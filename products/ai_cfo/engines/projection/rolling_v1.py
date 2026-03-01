class RollingCashflowV1:

    def __init__(self, hooks: dict | None = None):
        """
        hooks: {
            "pre_projection": callable(snapshot) -> snapshot,
            "pre_revenue": callable(revenue, month, context) -> revenue,
            "post_projection": callable(result) -> result
        }
        """
        self.hooks = hooks or {}

    def _apply_hook(self, name, *args, **kwargs):
        hook = self.hooks.get(name)
        if callable(hook):
            return hook(*args, **kwargs)
        return None

    def run(self, snapshot: dict, months: int = 12, adjustments: dict | None = None):

        adjustments = adjustments or {}

        # 🔹 Hook 1: pre_projection (允許調整 snapshot，但不可改結構)
        modified_snapshot = self._apply_hook("pre_projection", snapshot)
        if modified_snapshot:
            snapshot = modified_snapshot

        monthly_revenue = snapshot["monthly_revenue"]
        fixed_cost = snapshot["fixed_cost"]
        variable_ratio = snapshot["variable_cost_ratio"]
        cash = snapshot["cash_on_hand"]
        ar_days = snapshot["ar_days"]
        bad_debt = snapshot["bad_debt_ratio"]
        loan_payment = snapshot["loan_monthly_payment"]

        growth = adjustments.get("growth_rate", 0.0)

        delay_months = int(ar_days / 30)

        revenue_history = []
        collection_queue = []
        cash_history = []
        collection_history = []

        for month in range(months):

            # Revenue growth (compound)
            if month == 0:
                revenue = monthly_revenue
            else:
                revenue = revenue_history[-1] * (1 + growth)

            # 🔹 Hook 2: pre_revenue (允許對 revenue 做調整，例如季節性)
            modified_revenue = self._apply_hook(
                "pre_revenue",
                revenue,
                month,
                {
                    "snapshot": snapshot,
                    "growth": growth
                }
            )

            if modified_revenue is not None:
                revenue = modified_revenue

            revenue_history.append(revenue)

            collection_queue.append(revenue)

            if month >= delay_months:
                collected = collection_queue[month - delay_months] * (1 - bad_debt)
            else:
                collected = 0

            collection_history.append(collected)

            variable_cost = revenue * variable_ratio

            cash = (
                cash
                + collected
                - fixed_cost
                - variable_cost
                - loan_payment
            )

            cash_history.append(cash)

        lowest_cash = min(cash_history)
        negative_month = next((i+1 for i, v in enumerate(cash_history) if v < 0), None)
        runway = negative_month if negative_month else months

        result = {
            "monthly_cash_balance": cash_history,
            "monthly_revenue": revenue_history,
            "monthly_collections": collection_history,
            "runway_months": runway,
            "lowest_cash_point": lowest_cash,
            "negative_month": negative_month
        }

        # 🔹 Hook 3: post_projection (允許分析或增加額外欄位)
        modified_result = self._apply_hook("post_projection", result)
        if modified_result:
            result = modified_result

        return result