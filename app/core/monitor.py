import asyncio
import logging
try:
    from kubernetes import client, config
except Exception:
    client = None
    config = None

logger = logging.getLogger(__name__)

class LogMonitor:
    def __init__(self, orchestrator, interval=60, namespace="default"):
        self.orchestrator = orchestrator
        self.interval = interval
        self.namespace = namespace
        self._running = False
        self.api = None
        
        # Try to load kube config
        try:
            if config:
                try:
                    config.load_incluster_config()
                except Exception:
                    config.load_kube_config()
                self.api = client.CoreV1Api()
        except Exception:
            self.api = None

    async def start(self):
        self._running = True
        logger.info("LogMonitor started")
        asyncio.create_task(self._loop())

    async def stop(self):
        self._running = False
        logger.info("LogMonitor stopped")

    async def _loop(self):
        while self._running:
            try:
                if self.api:
                    await self._scan_pods()
                else:
                    logger.warning("LogMonitor: No K8s connection (dry-run)")
            except Exception as e:
                logger.error(f"LogMonitor error: {e}")
            
            await asyncio.sleep(self.interval)

    async def _scan_pods(self):
        logger.info(f"Scanning pods in {self.namespace}...")
        try:
            pods = self.api.list_namespaced_pod(self.namespace)
            for pod in pods.items:
                name = pod.metadata.name
                # Fetch last few lines
                try:
                    logs = self.api.read_namespaced_pod_log(name, self.namespace, tail_lines=20)
                    if self._analyze_logs(logs):
                        logger.info(f"Issue found in {name}, triggering incident...")
                        incident = {
                            "source": "LogMonitor",
                            "severity": "critical", # Assume critical if error found
                            "details": {
                                "msg": "Error detected in logs",
                                "pod": name,
                                "namespace": self.namespace,
                                "snippet": logs[-200:] if logs else ""
                            }
                        }
                        await self.orchestrator.process_incident(incident)
                except Exception as e:
                    logger.warning(f"Could not read logs for {name}: {e}")
        except Exception as e:
            logger.error(f"Failed to list pods: {e}")

    def _analyze_logs(self, logs: str) -> bool:
        # Simple keyword matching for now
        keywords = ["Error", "Exception", "Critical", "OOMKilled", "CrashLoopBackOff"]
        return any(k in logs for k in keywords)
