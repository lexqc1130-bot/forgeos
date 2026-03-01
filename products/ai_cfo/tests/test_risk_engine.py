from products.ai_cfo.engines.risk.scoring_v1 import RiskScoringV1
from products.ai_cfo.engines.risk.risk_profile import SMERiskProfile


engine = RiskScoringV1(SMERiskProfile())


def test_healthy_company():

    snapshot = {
        "cash": 1000000,
        "monthly_burn": 50000,
        "monthly_revenue": 200000,
        "total_debt": 100000,
        "total_assets": 1000000,
        "last_6_month_revenue": [200000, 210000, 190000, 205000, 195000, 200000]
    }

    result = engine.run(snapshot)

    assert result["current"]["final_level"] == "LOW"


def test_medium_risk_company():

    snapshot = {
        "cash": 200000,
        "monthly_burn": 70000,
        "monthly_revenue": 80000,
        "total_debt": 400000,
        "total_assets": 800000,
        "last_6_month_revenue": [80000, 85000, 75000, 82000, 78000, 81000]
    }

    result = engine.run(snapshot)

    assert result["current"]["final_level"] in ["MEDIUM", "HIGH"]


def test_three_high_fragility():

    snapshot = {
        "cash": 100000,
        "monthly_burn": 60000,
        "monthly_revenue": 30000,
        "total_debt": 900000,
        "total_assets": 1000000,
        "last_6_month_revenue": [30000, 20000, 40000, 15000, 35000, 10000]
    }

    result = engine.run(snapshot)

    assert result["current"]["fragility_multiplier"] == 1.5


def test_liquidity_burn_special_case():

    snapshot = {
        "cash": 100000,
        "monthly_burn": 60000,
        "monthly_revenue": 30000,
        "total_debt": 100000,
        "total_assets": 1000000,
        "last_6_month_revenue": [30000, 31000, 29000, 30500, 29500, 30000]
    }

    result = engine.run(snapshot)

    assert result["current"]["fragility_multiplier"] == 1.4


def test_projection_deteriorating():

    current_snapshot = {
        "cash": 500000,
        "monthly_burn": 50000,
        "monthly_revenue": 200000,
        "total_debt": 100000,
        "total_assets": 1000000,
        "last_6_month_revenue": [200000, 210000, 195000, 205000, 198000, 202000]
    }

    projected_snapshot = {
        "cash": 100000,
        "monthly_burn": 80000,
        "monthly_revenue": 40000,
        "total_debt": 800000,
        "total_assets": 900000,
        "last_6_month_revenue": [40000, 30000, 35000, 25000, 45000, 20000]
    }

    result = engine.run(current_snapshot, projected_snapshot)

    assert result["trend"] == "DETERIORATING"