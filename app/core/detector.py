# Simple rule-based detector stub
class Detector:
    def evaluate(self, incident: dict):
        # Determine tier by simple heuristics. In real system use ML/rules.
        sev = incident.get("severity", "").lower()
        if sev in ("critical", "sev3", "severity3", "tier-3"):
            tier = "tier-3"
            plan = {"actions": [{"type": "restart_pod", "namespace": "default", "pod_name": incident.get("details", {}).get("pod")} ]}
        else:
            tier = "tier-1-2"
            plan = {}
        return tier, plan
