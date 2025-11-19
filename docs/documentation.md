# AI-Ops-Remediator Documentation

## Overview

**AI-Ops-Remediator** is a self-healing automation platform designed to detect, analyze, and automatically remediate system and infrastructure failures using a microservices architecture. The project leverages **Python**, **FastAPI**, **Docker**, **Kubernetes**, **Slack**, **ServiceNow**, and **Gemini (LLM)** for automated insights.

AI-Ops-Remediator categorizes incidents into tiers:

* **Tier-3:** Automatically remediated without human intervention.
* **Tier-1/2:** Escalated to Slack and ServiceNow.

The system supports:

* Automatic detection of failures
* Automated remediation workflows
* AI-based log analysis using Google Gemini
* Notifications and escalations
* Kubernetes-native deployments

---

## Architecture

### Core Components

1. **Monitor (future extension):** Collects logs, metrics, events.
2. **Detector:** Determines incident severity and remediation plan.
3. **Remediator:** Runs actions such as pod restarts, scaling, config resets.
4. **Orchestrator:** Coordinates detection, remediation, and escalation.
5. **Notifier:** Sends alerts to Slack and creates ServiceNow tickets.
6. **Insights (LLM):** Uses Gemini to analyze logs and suggest fixes.

### Flow

1. Services send incidents/logs to AI-Ops-Remediator.
2. AI-Ops-Remediator evaluates severity using `Detector`.
3. If Tier-3:

   * The `Remediator` executes Kubernetes actions.
4. If Tier-1/2 or remediation fails:

   * `Notifier` escalates to Slack/ServiceNow.
5. Gemini analyzes logs to improve remediation accuracy.

---

## Technology Stack

* **Python 3.11** — Microservice logic
* **FastAPI** — API layer
* **Docker** — Containerization
* **Kubernetes** — Deployment, scaling, HA
* **Slack SDK** — Alerts
* **ServiceNow REST API** — Ticketing
* **Google Gemini** — Log analysis and remediation suggestions
* **pytest** — Testing

---

## Key Directories

```
AI-Ops-Remediator/
├─ app/
│  ├─ api/              # API endpoints
│  ├─ core/             # Main logic modules
│  ├─ schemas.py        # Request/response models
│  └─ main.py           # FastAPI application
├─ k8s/                 # Kubernetes manifests
├─ playbooks/           # Sample remediation playbooks
├─ tests/               # Unit tests
├─ Dockerfile           # Build image
├─ requirements.txt     # Python dependencies
└─ README.md            # Overview
```

---

## Key Modules Explained

### 1. Orchestrator

Central controller that:

* Starts services
* Processes incidents
* Calls detection, remediation, notifications
* Ensures safe and idempotent execution

### 2. Detector

Simple rules determine the tier based on severity keywords.
Advanced ML-based analysis can be integrated later.

### 3. Remediator

Handles Kubernetes actions like:

* Restarting pods
* Scaling deployments
* Dry-run mode if Kubernetes not available locally

### 4. Notifier

* Posts incident details to Slack
* Creates and updates ServiceNow tickets

### 5. Insights (Gemini)

LLM that:

* Reads logs and context
* Finds root cause
* Suggests remediation actions
* Outputs **validated JSON** for safe auto-execution

---

## Setup Instructions

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Set Gemini API key

```
setx GEMINI_API_KEY "your_key_here"  # Windows
echo "export GEMINI_API_KEY=your_key_here" >> ~/.bashrc  # Linux/macOS
```

### 3. Run locally

```
uvicorn app.main:app --reload --port 8000
```

### 4. Docker

```
docker build -t AI-Ops-Remediator:dev .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key AI-Ops-Remediator:dev
```

### 5. Kubernetes Deployment

```
kubectl apply -f k8s/
```

---

## Sending an Incident

```
curl -X POST http://localhost:8000/api/v1/incidents/ \n  -H "Content-Type: application/json" \n  -d '{
        "source": "service-x",
        "severity": "critical",
        "details": {"msg": "OOMKilled", "pod": "worker-123"}
      }'
```

---

## Future Extensions

* Prometheus metrics exporter
* More remediation playbooks
* Gemini-powered anomaly detection
* Multi-cloud remediation actions
* Distributed scheduler for periodic checks

---

## Summary

AI-Ops-Remediator is a modular, extensible, and AI-powered automation engine designed for modern SRE teams. It reduces manual intervention, improves MTTR, and enables proactive system healing using LLM-backed intelligence.
