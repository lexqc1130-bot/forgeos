from products.ai_cfo.services.risk_service import RiskService


service = RiskService()


def base_snapshot():
    return {
        "cash": 500000,
        "monthly_burn": 50000,
        "monthly_revenue": 200000,
        "total_debt": 100000,
        "total_assets": 1000000,
        "last_6_month_revenue": [200000] * 6
    }


def test_evaluate_returns_structure():

    result = service.evaluate(base_snapshot())

    assert "risk" in result
    assert "warning" in result

    assert "current" in result["risk"]
    assert "components" in result["risk"]["current"]
    assert "final_score" in result["risk"]["current"]


def test_simulate_changes_score():

    result = service.simulate(
        base_snapshot(),
        revenue_change=-0.3
    )

    assert "original" in result
    assert "scenario" in result
    assert result["delta_score"] >= 0


def test_projection_through_service():

    snapshot = base_snapshot()

    projected = snapshot.copy()
    projected["monthly_revenue"] *= 0.5

    result = service.evaluate(snapshot, projected)

    assert result["risk"]["trend"] in [
        "STABLE",
        "IMPROVING",
        "DETERIORATING"
    ]