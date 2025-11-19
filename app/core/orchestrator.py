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
        tier, plan = self.detector.evaluate(incident)
        if tier == "tier-3" and plan:
            result = await self.remediator.execute(plan)
            if result.get("success"):
                # record metric or audit log in real system
                return {"action": "auto_remediated", "details": result}
            else:
                ticket = self.notifier.escalate(incident, result)
                return {"action": "escalated", "ticket": ticket}
        else:
            ticket = self.notifier.escalate(incident, {"reason": "non-auto"})
            return {"action": "escalated", "ticket": ticket}
