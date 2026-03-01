from products.ai_cfo.engines.risk.scoring_v1 import RiskScoringV1
from products.ai_cfo.engines.risk.risk_profile import SMERiskProfile
from products.ai_cfo.services.scenario_simulator import ScenarioSimulator
from products.ai_cfo.services.warning_engine import WarningEngine
from products.ai_cfo.services.policy.intervention_policy import InterventionPolicy

class RiskService:

    def __init__(self, profile=None):
        profile = profile or SMERiskProfile()
        self.engine = RiskScoringV1(profile)
        self.simulator = ScenarioSimulator(self.engine)
        self.warning_engine = WarningEngine()
        self.policy = InterventionPolicy(profile)

    def evaluate(self, snapshot, projection=None):
        risk = self.engine.run(snapshot, projection)
        warning = self.warning_engine.analyze(risk)

        return {
            "risk": risk,
            "warning": warning
        }

    def simulate(self, snapshot, **kwargs):
        return self.simulator.simulate(snapshot, **kwargs)
    
    def evaluate_with_policy(self, snapshot, projection=None):

        result = self.evaluate(snapshot, projection)
        intervention = self.policy.evaluate(result)

        return {
            **result,
            "intervention_state": intervention.value
        }