from products.ai_cfo.services.risk_service import RiskService
from products.ai_cfo.services.decision_engine import DecisionEngine


service = RiskService()
engine = DecisionEngine(service)


def test_decision_engine_finds_plan():

    snapshot = {
        "cash": 100000,
        "monthly_burn": 60000,
        "monthly_revenue": 30000,
        "total_debt": 900000,
        "total_assets": 1000000,
        "last_6_month_revenue": [30000] * 6
    }

    result = engine.find_improvement_plan(snapshot)

    assert "actions" in result