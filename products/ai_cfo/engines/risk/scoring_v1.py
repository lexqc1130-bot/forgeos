class RiskScoringV1:

    def __init__(self, profile):
        self.profile = profile

    # =====================================================
    # Public API
    # =====================================================

    def run(self, snapshot, projection=None):

        current = self._calculate(snapshot)

        if projection:
            projected = self._calculate(projection)
            trend = self._trend(
                current["final_score"],
                projected["final_score"]
            )
        else:
            projected = None
            trend = None

        return {
            "current": current,
            "projected": projected,
            "trend": trend
        }

    # =====================================================
    # Core Calculation
    # =====================================================

    def _calculate(self, data):

        liquidity = self._liquidity(data)
        burn = self._burn(data)
        debt = self._debt(data)
        revenue_stability = self._revenue_stability(data)

        fragility = self._fragility_multiplier(
            liquidity["level"],
            burn["level"],
            debt["level"]
        )

        base_score = max(
            liquidity["score"],
            burn["score"],
            debt["score"],
            revenue_stability["score"]
        )

        final_score = min(int(base_score * fragility), 100)
        final_level = self._score_to_level(final_score)

        return {
            "components": {
                "liquidity": liquidity,
                "burn": burn,
                "debt": debt,
                "revenue_stability": revenue_stability
            },
            "fragility_multiplier": fragility,
            "final_score": final_score,
            "final_level": final_level
        }

    # =====================================================
    # Component Calculations
    # =====================================================

    def _liquidity(self, data):
        cash = data.get("cash", 0)
        burn = data.get("monthly_burn", 0)

        runway = cash / burn if burn > 0 else 999

        if runway < self.profile.runway_high_risk:
            return {"level": "HIGH", "score": 80}
        elif runway < self.profile.runway_medium_risk:
            return {"level": "MEDIUM", "score": 55}
        else:
            return {"level": "LOW", "score": 25}

    def _burn(self, data):
        burn = data.get("monthly_burn", 0)
        revenue = data.get("monthly_revenue", 0)

        ratio = burn / revenue if revenue > 0 else 1.5

        if ratio > self.profile.burn_high_risk:
            return {"level": "HIGH", "score": 85}
        elif ratio > self.profile.burn_medium_risk:
            return {"level": "MEDIUM", "score": 60}
        else:
            return {"level": "LOW", "score": 30}

    def _debt(self, data):
        debt = data.get("total_debt", 0)
        assets = data.get("total_assets", 0)

        ratio = debt / assets if assets > 0 else 1

        if ratio > self.profile.debt_high_risk:
            return {"level": "HIGH", "score": 75}
        elif ratio > self.profile.debt_medium_risk:
            return {"level": "MEDIUM", "score": 50}
        else:
            return {"level": "LOW", "score": 20}

    def _revenue_stability(self, data):

        revenues = data.get("last_6_month_revenue", [])

        if not revenues or len(revenues) < 2:
            return {"level": "LOW", "score": 20}

        mean = sum(revenues) / len(revenues)
        variance = sum((x - mean) ** 2 for x in revenues) / len(revenues)
        std = variance ** 0.5

        volatility = std / mean if mean > 0 else 1

        if volatility > self.profile.revenue_vol_high:
            return {"level": "HIGH", "score": 80}
        elif volatility > self.profile.revenue_vol_medium:
            return {"level": "MEDIUM", "score": 55}
        else:
            return {"level": "LOW", "score": 25}

    # =====================================================
    # Fragility Logic
    # =====================================================

    def _fragility_multiplier(self, l, b, d):
        high_count = [l, b, d].count("HIGH")

        if high_count == 3:
            return 1.5
        elif l == "HIGH" and b == "HIGH":
            return 1.4
        elif high_count == 2:
            return 1.3
        else:
            return 1.0

    # =====================================================
    # Utility
    # =====================================================

    def _score_to_level(self, score):
        if score >= 70:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        return "LOW"

    def _trend(self, current_score, projected_score):

        if projected_score > current_score + 10:
            return "DETERIORATING"
        elif projected_score < current_score - 10:
            return "IMPROVING"
        else:
            return "STABLE"