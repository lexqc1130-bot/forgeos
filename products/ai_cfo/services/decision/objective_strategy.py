class ObjectiveStrategy:

    def choose(self, base_level, candidates):
        """
        candidates = list of dict:
        {
            "strategy": ...,
            "new_level": ...,
            "cost": ...
        }
        """
        raise NotImplementedError


class WeightedObjective:

    def __init__(self, risk_weight=2.0, cost_weight=1.0):
        self.risk_weight = risk_weight
        self.cost_weight = cost_weight

    def choose(self, base_level, candidates):

        if not candidates:
            return None

        def utility(c):
            risk_improvement = -c["score_delta"]
            return (risk_improvement * self.risk_weight) - (c["cost"] * self.cost_weight)

        return max(candidates, key=utility)