import asyncio
from app.core.detector import Detector
from app.core.remediator import Remediator
from app.core.notifier import Notifier

class Orchestrator:
    def __init__(self):
        self.detector = Detector()
        self.remediator = Remediator()
        self.notifier = Notifier()
        self._running = False

    async def start(self):
        self._running = True
        print("Orchestrator started")


    async def stop(self):
        self._running = False
        print("Orchestrator stopped")

    async def process_incident(self, incident: dict):
        # 1. Fetch logs if pod info is available
        details = incident.get("details", {})
        pod_name = details.get("pod")
        namespace = details.get("namespace", "default")
        logs = ""
        
        if pod_name:
            logs = self.remediator.get_pod_logs(namespace, pod_name)
            print(f"Fetched logs for {pod_name}: {len(logs)} chars")

        # 2. Analyze with GenAI if logs exist
        analysis = {}
        if logs and "dry-run" not in logs:
            from app.core.insights import GenAIInsights
            try:
                insights = GenAIInsights()
                analysis = insights.analyze(logs, incident)
                print("GenAI Analysis:", analysis)
            except Exception as e:
                print(f"GenAI failed: {e}")

        # 3. Evaluate and Remediate
        tier, plan = self.detector.evaluate(incident)
        
        # AI-FIRST STRATEGY
        # If Gemini is confident (>0.8), we prioritize its plan over the static detector.
        ai_confidence = analysis.get("confidence", 0.0)
        ai_actions = analysis.get("suggested_actions", [])
        
        if ai_confidence >= 0.8 and ai_actions:
            print(f"AI Confidence {ai_confidence} >= 0.8. Executing AI Plan.")
            tier = "tier-3" # Force execution
            plan = {"actions": ai_actions}
        elif ai_actions:
            print(f"AI Confidence {ai_confidence} too low. Escalating with suggestions.")
            # We don't execute, but we pass the analysis to the ticket.

        if tier == "tier-3" and plan:
            result = await self.remediator.execute(plan)
            result["analysis"] = analysis
            if result.get("success"):
                return {"action": "auto_remediated", "details": result}
            else:
                # If remediation failed (even AI's), we escalate.
                ticket = self.notifier.escalate(incident, result)
                return {"action": "escalated_after_failure", "ticket": ticket}
        else:
            # Low confidence AND no rule-based plan -> Ticket
            ticket = self.notifier.escalate(incident, {"reason": "low_confidence_or_unknown", "analysis": analysis})
            return {"action": "escalated", "ticket": ticket}
