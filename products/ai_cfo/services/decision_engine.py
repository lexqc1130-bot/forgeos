class DecisionEngine:

    def __init__(self, risk_service):
        self.service = risk_service

    def find_improvement_plan(self, snapshot):

        base_result = self.service.evaluate(snapshot)
        base_level = base_result["risk"]["current"]["final_level"]

        if base_level == "LOW":
            return {
                "message": "No action required",
                "actions": []
            }

        # 1️⃣ 試 revenue 提升
        for change in [0.05 * i for i in range(1, 11)]:  # 5% → 50%
            result = self.service.simulate(snapshot, revenue_change=change)
            new_level = result["scenario"]["current"]["final_level"]

            if self._is_improved(base_level, new_level):
                return {
                    "actions": [
                        {
                            "type": "increase_revenue",
                            "change": change,
                            "expected_level": new_level
                        }
                    ]
                }

        # 2️⃣ 試 burn 降低
        for change in [-0.05 * i for i in range(1, 11)]:
            result = self.service.simulate(snapshot, burn_change=change)
            new_level = result["scenario"]["current"]["final_level"]

            if self._is_improved(base_level, new_level):
                return {
                    "actions": [
                        {
                            "type": "reduce_burn",
                            "change": change,
                            "expected_level": new_level
                        }
                    ]
                }

        # 3️⃣ 試現金注入
        for cash in [100000 * i for i in range(1, 21)]:
            result = self.service.simulate(snapshot, cash_shock=cash)
            new_level = result["scenario"]["current"]["final_level"]

            if self._is_improved(base_level, new_level):
                return {
                    "actions": [
                        {
                            "type": "raise_cash",
                            "amount": cash,
                            "expected_level": new_level
                        }
                    ]
                }

        return {
            "message": "No simple improvement found",
            "actions": []
        }

    def _is_improved(self, old_level, new_level):
        order = ["LOW", "MEDIUM", "HIGH"]
        return order.index(new_level) < order.index(old_level)