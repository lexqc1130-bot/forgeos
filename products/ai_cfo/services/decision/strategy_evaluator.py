class StrategyEvaluator:

    def __init__(self, risk_service):
        self.service = risk_service

    def evaluate(self, snapshot, strategy):

        base = self.service.evaluate(snapshot)
        base_score = base["risk"]["current"]["final_score"]

        result = self.service.simulate(snapshot, **strategy)
        scenario = result["scenario"]["current"]

        new_score = scenario["final_score"]
        new_level = scenario["final_level"]

        return {
            "level": new_level,
            "score": new_score,
            "score_delta": new_score - base_score
        }