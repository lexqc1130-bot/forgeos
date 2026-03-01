class WarningEngine:

    def analyze(self, risk_result):

        alerts = []
        severity = "LOW"

        current = risk_result["current"]
        level = current["final_level"]
        fragility = current["fragility_multiplier"]
        trend = risk_result.get("trend")

        # -----------------------
        # 基本風險等級
        # -----------------------
        if level == "HIGH":
            alerts.append("Overall risk level is HIGH")
            severity = "HIGH"

        elif level == "MEDIUM":
            alerts.append("Overall risk level is MEDIUM")
            severity = "MEDIUM"

        # -----------------------
        # Fragility 放大
        # -----------------------
        if fragility >= 1.4:
            alerts.append("Structural fragility detected")
            severity = "HIGH"

        # -----------------------
        # 趨勢惡化
        # -----------------------
        if trend == "DETERIORATING":
            alerts.append("Risk trend is deteriorating")
            severity = "HIGH"

        return {
            "severity": severity,
            "alerts": alerts
        }