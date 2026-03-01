from products.ai_cfo.engines.risk.scoring_v1 import RiskScoringV1
from products.ai_cfo.engines.risk.risk_profile import SMERiskProfile
from products.ai_cfo.services.scenario_simulator import ScenarioSimulator


engine = RiskScoringV1(SMERiskProfile())
simulator = ScenarioSimulator(engine)


def test_revenue_drop_increases_risk():

    snapshot = {
        "cash": 500000,
        "monthly_burn": 50000,
        "monthly_revenue": 200000,
        "total_debt": 100000,
        "total_assets": 1000000,
        "last_6_month_revenue": [200000]*6
    }

    result = simulator.simulate(snapshot, revenue_change=-0.3)

    assert result["delta_score"] >= 0