class RollingCashflowV1:

    def run(self, snapshot: dict, months: int = 12, adjustments: dict | None = None):

        adjustments = adjustments or {}

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

            revenue_history.append(revenue)

            # Add to AR queue
            collection_queue.append(revenue)

            # Collect delayed revenue
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

        return {
            "monthly_cash_balance": cash_history,
            "monthly_revenue": revenue_history,
            "monthly_collections": collection_history,
            "runway_months": runway,
            "lowest_cash_point": lowest_cash,
            "negative_month": negative_month
        }