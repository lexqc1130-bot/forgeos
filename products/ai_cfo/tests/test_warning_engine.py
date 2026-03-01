from products.ai_cfo.services.risk_service import RiskService


service = RiskService()


def test_high_risk_generates_warning():

    snapshot = {
        "cash": 100000,
        "monthly_burn": 60000,
        "monthly_revenue": 30000,
        "total_debt": 900000,
        "total_assets": 1000000,
        "last_6_month_revenue": [30000]*6
    }

    result = service.evaluate(snapshot)

    assert result["warning"]["severity"] == "HIGH"