from app.core.orchestrator import Orchestrator
from app.core.monitor import LogMonitor

orchestrator = Orchestrator()
monitor = LogMonitor(orchestrator)
