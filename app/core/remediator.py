import asyncio
try:
    from kubernetes import client, config
except Exception:
    client = None
    config = None

class Remediator:
    def __init__(self):
        self.api = None
        # Try to load kube config if available; if not, we operate in a dry-run mode.
        try:
            if config:
                try:
                    config.load_incluster_config()
                except Exception:
                    config.load_kube_config()
                self.api = client.CoreV1Api()
        except Exception:
            self.api = None

    async def execute(self, plan: dict):
        actions = plan.get("actions", [])
        results = []
        for a in actions:
            if a.get("type") == "restart_pod":
                ns = a.get("namespace", "default")
                pod = a.get("pod_name")
                if not pod:
                    results.append({"error": "no pod specified"})
                    continue
                if self.api:
                    try:
                        # delete pod to trigger restart by controller
                        self.api.delete_namespaced_pod(pod, ns)
                        results.append({"pod": pod, "status": "deleted"})
                    except Exception as e:
                        results.append({"pod": pod, "error": str(e)})
                else:
                    results.append({"pod": pod, "status": "dry-run - would delete"})
            
            elif a.get("type") == "scale":
                ns = a.get("namespace", "default")
                dep = a.get("deployment_name") or a.get("pod_name") # Fallback if AI is fuzzy
                replicas = int(a.get("value", 1))
                
                if not dep:
                     results.append({"error": "no deployment specified"})
                     continue
                
                if self.api:
                    try:
                        # We need AppsV1Api for deployments
                        apps_api = client.AppsV1Api()
                        # Patch the deployment
                        patch = {"spec": {"replicas": replicas}}
                        apps_api.patch_namespaced_deployment_scale(dep, ns, patch)
                        results.append({"deployment": dep, "status": f"scaled to {replicas}"})
                    except Exception as e:
                         results.append({"deployment": dep, "error": str(e)})
                else:
                    results.append({"deployment": dep, "status": f"dry-run - would scale to {replicas}"})

            else:
                results.append({"error": f"unsupported action type: {a.get('type')}"})

        success = all("error" not in r for r in results)
        return {"success": success, "results": results}

    def get_pod_logs(self, namespace: str, pod_name: str, tail_lines: int = 50) -> str:
        if not self.api:
            return "Logs unavailable (dry-run mode)"
        try:
            return self.api.read_namespaced_pod_log(name=pod_name, namespace=namespace, tail_lines=tail_lines)
        except Exception as e:
            return f"Failed to fetch logs: {str(e)}"
