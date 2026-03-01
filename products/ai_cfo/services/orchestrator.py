from products.ai_cfo.services.decision.decision_engine_v2 import DecisionEngineV2
from products.ai_cfo.services.policy.intervention_memory import InterventionMemory


class AICFOOrchestrator:

    def __init__(self, risk_service, depth=2):
        self.risk_service = risk_service
        self.decision_engine = DecisionEngineV2(risk_service, depth=depth)
        self.memory = InterventionMemory()

    def evaluate(self, snapshot, projection=None):

        # 1️⃣ 先跑風險 + policy
        result = self.risk_service.evaluate_with_policy(snapshot, projection)

        state = result["intervention_state"]
        stage = self.risk_service.engine.profile.stage

        # 2️⃣ 更新記憶
        current_level = result["risk"]["current"]["final_level"]
        self.memory.update(current_level)

        recommended_strategy = None

        # -------------------------
        # Escalation Matrix
        # -------------------------

        if state == "CRITICAL":
            recommended_strategy = self.decision_engine.find_best_strategy(snapshot)

        elif state == "INTERVENTION":
            recommended_strategy = self.decision_engine.find_best_strategy(snapshot)

        elif state == "PREVENTIVE":

            if stage in ["stable", "distressed"]:
                recommended_strategy = self.decision_engine.find_best_strategy(snapshot)

            # growth 在 preventive 只提示，不自動

        # -------------------------
        # 🔥 Memory-based override
        # -------------------------
        # 連續兩次惡化 → 強制升級干預

        if self.memory.deterioration_count >= 2:
            recommended_strategy = self.decision_engine.find_best_strategy(snapshot)

        return {
            **result,
            "recommended_strategy": recommended_strategy,
            "memory_state": {
                "deterioration_count": self.memory.deterioration_count,
                "improvement_count": self.memory.improvement_count
            }
        }