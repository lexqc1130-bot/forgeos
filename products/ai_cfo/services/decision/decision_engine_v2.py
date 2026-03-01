from products.ai_cfo.services.decision.brute_force_strategy import BruteForceStrategy
from products.ai_cfo.services.decision.strategy_evaluator import StrategyEvaluator
from products.ai_cfo.services.decision.cost_model import CostModel
from products.ai_cfo.services.decision.objective_selector import ObjectiveSelector
from products.ai_cfo.services.decision.search_budget import SearchBudgetPolicy


class DecisionEngineV2:

    def __init__(self,
                 risk_service,
                 depth=1,
                 max_evaluations=200,
                 override_mode=None):

        self.service = risk_service
        self.strategy = BruteForceStrategy(depth=depth)
        self.evaluator = StrategyEvaluator(risk_service)
        self.cost_model = CostModel()

        # 仍保留硬上限保護
        self.hard_max_evaluations = max_evaluations

        # 🔥 人格選擇器現在會接 profile
        profile = risk_service.engine.profile
        self.selector = ObjectiveSelector(
            profile=profile,
            override_mode=override_mode
        )

    def find_best_strategy(self, snapshot):

        base_result = self.service.evaluate(snapshot)

        current = base_result["risk"]["current"]
        base_level = current["final_level"]
        fragility = current["fragility_multiplier"]

        # 🔥 動態搜尋預算（依 risk level）
        budget_policy = SearchBudgetPolicy(base_level)
        dynamic_budget = budget_policy.max_evaluations()

        max_evaluations = min(dynamic_budget, self.hard_max_evaluations)

        candidates = []
        evaluations = 0

        for strategy in self.strategy.generate():

            if evaluations >= max_evaluations:
                break

            evaluations += 1

            evaluation = self.evaluator.evaluate(snapshot, strategy)
            new_level = evaluation["level"]

            if self._is_improved(base_level, new_level):

                cost = self.cost_model.evaluate(strategy)

                candidates.append({
                    "strategy": strategy,
                    "new_level": new_level,
                    "cost": cost,
                    "score_delta": evaluation["score_delta"]
                })

        # 🔥 由 selector 根據 profile × risk × fragility 動態產生權重
        objective = self.selector.select(
            base_level=base_level,
            fragility=fragility
        )

        return objective.choose(base_level, candidates)

    def _is_improved(self, old, new):
        order = ["LOW", "MEDIUM", "HIGH"]
        return order.index(new) < order.index(old)