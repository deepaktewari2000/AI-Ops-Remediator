# AI-Ops-Remediator

Self-healing microservice platform — Python · FastAPI · Docker · Kubernetes · Slack · ServiceNow · GenAI

This is a starter scaffold with core components so you can run locally or deploy into Kubernetes.
See `app/` for the code, `k8s/` for manifests, and `.github/` for a CI example.

Quick start (dev)
1. Build image: `docker build -t AI-Ops-Remediator:dev .`
2. Run locally: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`
3. Post an incident: `curl -X POST http://localhost:8000/api/v1/incidents/ -H 'Content-Type: application/json' -d '{"source":"test","severity":"critical","details":{"msg":"oom"}}'`
