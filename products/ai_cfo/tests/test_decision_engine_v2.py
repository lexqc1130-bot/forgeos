from products.ai_cfo.services.risk_service import RiskService
from products.ai_cfo.services.decision.decision_engine_v2 import DecisionEngineV2


service = RiskService()
engine = DecisionEngineV2(service, depth=2)


def test_v2_returns_strategy():

    snapshot = {
        "cash": 100000,
        "monthly_burn": 60000,
        "monthly_revenue": 30000,
        "total_debt": 900000,
        "total_assets": 1000000,
        "last_6_month_revenue": [30000] * 6
    }

    result = engine.find_best_strategy(snapshot)

    assert result is None or "strategy" in result