class StrategyGenerator:

    def generate(self):
        for revenue in [0.05 * i for i in range(1, 6)]:
            yield {"revenue_change": revenue}

        for burn in [-0.05 * i for i in range(1, 6)]:
            yield {"burn_change": burn}

        for cash in [100000 * i for i in range(1, 6)]:
            yield {"cash_shock": cash}