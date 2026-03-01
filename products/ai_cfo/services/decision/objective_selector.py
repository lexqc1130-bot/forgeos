from products.ai_cfo.services.decision.objective_strategy import WeightedObjective


class ObjectiveSelector:

    def __init__(self, profile, override_mode=None):
        self.profile = profile
        self.override_mode = override_mode

    def select(self, base_level, fragility):

        if self.override_mode:
            return self._override_objective()

        risk_weight, cost_weight = self.profile.decision_weights(
            base_level,
            fragility
        )

        return WeightedObjective(
            risk_weight=risk_weight,
            cost_weight=cost_weight
        )