from itertools import combinations


class BruteForceStrategy:

    def __init__(self, depth=1):
        self.depth = depth

        self.base_dimensions = {
            "revenue_change": [0.05 * i for i in range(1, 6)],
            "burn_change": [-0.05 * i for i in range(1, 6)],
            "cash_shock": [100000 * i for i in range(1, 6)],
        }

    def generate(self):

        keys = list(self.base_dimensions.keys())

        for r in range(1, self.depth + 1):
            for combo in combinations(keys, r):

                yield from self._generate_combinations(combo)

    def _generate_combinations(self, keys):

        if len(keys) == 1:
            key = keys[0]
            for value in self.base_dimensions[key]:
                yield {key: value}

        elif len(keys) == 2:
            k1, k2 = keys
            for v1 in self.base_dimensions[k1]:
                for v2 in self.base_dimensions[k2]:
                    yield {k1: v1, k2: v2}

        elif len(keys) == 3:
            k1, k2, k3 = keys
            for v1 in self.base_dimensions[k1]:
                for v2 in self.base_dimensions[k2]:
                    for v3 in self.base_dimensions[k3]:
                        yield {k1: v1, k2: v2, k3: v3}