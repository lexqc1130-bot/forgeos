class CostModel:

    def evaluate(self, strategy):
        cost = 0

        if "revenue_change" in strategy:
            cost += abs(strategy["revenue_change"]) * 10

        if "burn_change" in strategy:
            cost += abs(strategy["burn_change"]) * 5

        if "cash_shock" in strategy:
            cost += strategy["cash_shock"] / 100000

        return cost