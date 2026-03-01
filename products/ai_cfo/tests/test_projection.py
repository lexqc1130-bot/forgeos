from products.ai_cfo.engines.projection.rolling_v1 import RollingCashflowV1


def run_test():

    snapshot = {
        "monthly_revenue": 600000,
        "fixed_cost": 250000,
        "variable_cost_ratio": 0.3,
        "cash_on_hand": 800000,
        "ar_days": 30,
        "bad_debt_ratio": 0.02,
        "loan_monthly_payment": 50000
    }

    engine = RollingCashflowV1()

    result_12 = engine.run(snapshot, months=12, adjustments={"growth_rate": 0.00})
    result_18 = engine.run(snapshot, months=18, adjustments={"growth_rate": 0.00})
    result_24 = engine.run(snapshot, months=24, adjustments={"growth_rate": 0.00})

    print("=== 12 Months ===")
    print("Runway:", result_12["runway_months"])
    print("Lowest Cash:", result_12["lowest_cash_point"])
    print()

    print("=== 18 Months ===")
    print("Runway:", result_18["runway_months"])
    print("Lowest Cash:", result_18["lowest_cash_point"])
    print()

    print("=== 24 Months ===")
    print("Runway:", result_24["runway_months"])
    print("Lowest Cash:", result_24["lowest_cash_point"])
    print()


if __name__ == "__main__":
    run_test()