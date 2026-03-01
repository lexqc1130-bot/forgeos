from products.ai_cfo.services.policy.intervention_state import InterventionState


class InterventionPolicy:

    def __init__(self, profile):
        self.profile = profile

    def evaluate(self, risk_result):

        current = risk_result["risk"]["current"]
        trend = risk_result["risk"].get("trend")

        level = current["final_level"]
        fragility = current["fragility_multiplier"]

        # -------------------------
        # Base sensitivity (stage)
        # -------------------------
        sensitivity = 1.0

        if self.profile.stage == "growth":
            sensitivity = 0.8  # 較容忍風險

        elif self.profile.stage == "distressed":
            sensitivity = 1.3  # 非常敏感

        # -------------------------
        # Critical condition
        # -------------------------
        if level == "HIGH" and fragility >= 1.4:
            return InterventionState.CRITICAL

        # -------------------------
        # Intervention
        # -------------------------
        if level == "HIGH":
            return InterventionState.INTERVENTION

        # -------------------------
        # Preventive (trend-driven)
        # -------------------------
        if trend == "DETERIORATING":
            return InterventionState.PREVENTIVE

        return InterventionState.MONITOR