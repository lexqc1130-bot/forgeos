class InterventionMemory:

    def __init__(self):
        self.previous_level = None
        self.deterioration_count = 0
        self.improvement_count = 0

    def update(self, current_level):

        order = ["LOW", "MEDIUM", "HIGH"]

        if self.previous_level is None:
            self.previous_level = current_level
            return

        if order.index(current_level) > order.index(self.previous_level):
            self.deterioration_count += 1
            self.improvement_count = 0

        elif order.index(current_level) < order.index(self.previous_level):
            self.improvement_count += 1
            self.deterioration_count = 0

        else:
            # same level
            self.deterioration_count = 0
            self.improvement_count = 0

        self.previous_level = current_level