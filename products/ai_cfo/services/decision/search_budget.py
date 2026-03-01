class SearchBudgetPolicy:

    def __init__(self, risk_level):
        self.risk_level = risk_level

    def max_evaluations(self):

        if self.risk_level == "HIGH":
            return 300

        if self.risk_level == "MEDIUM":
            return 200

        return 100