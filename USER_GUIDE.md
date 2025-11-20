# AI-Ops-Remediator User Guide

This guide explains how to integrate **AI-Ops-Remediator** with your existing infrastructure, how the auto-remediation logic works, and how incidents are escalated to ServiceNow.

## 1. Integration: Sending Alerts

To use AI-Ops-Remediator, your monitoring system (Prometheus, Datadog, New Relic, etc.) must send alerts to the **Incidents API**.

### Endpoint
`POST /api/v1/incidents/`

### Payload Format
Your monitoring tool should send a webhook with the following JSON structure:

```json
{
  "source": "prometheus",
  "severity": "critical",
  "details": {
    "msg": "OOMKilled",
    "pod": "payment-service-789",
    "namespace": "production"
  }
}
```

| Field | Description |
| :--- | :--- |
| `source` | The origin of the alert (e.g., "prometheus", "cloudwatch"). |
| `severity` | Severity level. **"critical"** or **"tier-3"** triggers auto-remediation. |
| `details` | Dictionary containing context. Must include `pod` and `namespace` for K8s actions. |

---

## 2. How It Works

### Scenario A: Auto-Remediation (Tier-3)
**Trigger:** An incident with `severity: "critical"` or `severity: "tier-3"`.

1.  **Detection**: The system identifies this as a Tier-3 issue.
2.  **Action**: It looks for a remediation plan. For example, if the message contains "OOM", it might decide to restart the pod.
3.  **Execution**: The `Remediator` connects to your Kubernetes cluster and deletes the pod (forcing a restart).
4.  **Result**:
    *   **Success**: The incident is marked as resolved. No human is paged.
    *   **Failure**: If the pod fails to restart, the system escalates (see Scenario B).

### Scenario C: AI Insights (Log Analysis)
**Trigger:** Any incident that includes `pod` and `namespace` details.

1.  **Log Fetching**: The system automatically connects to the Kubernetes pod and retrieves the last 50 lines of logs.
2.  **Analysis**: These logs are sent to Google Gemini (if configured).
3.  **Output**: The AI identifies the root cause and suggests actions. This analysis is attached to the remediation result or the escalation ticket.

### Scenario D: Active Monitoring
**Trigger:** The system actively polls logs every 60 seconds.

1.  **Scanning**: The `LogMonitor` scans all pods in the default namespace.
2.  **Detection**: If it finds keywords like "Error" or "Exception", it automatically creates an incident.
3.  **Process**: This incident triggers the standard remediation flow (Scenario A/C).

### Scenario B: Escalation (Tier-1/2)
**Trigger:** An incident with `severity: "warning"` OR a failed remediation.

1.  **Notification**: The `Notifier` posts a message to your Slack channel (configured via `SLACK_CHANNEL`).
2.  **Ticketing**: The system calls the ServiceNow API to create a new Incident ticket.
    *   **Short Description**: "Escalation: prometheus - warning"
    *   **Description**: Full JSON details of the incident.
    *   **Urgency**: Set to "2".

### Scenario E: AI-Driven Auto-Remediation
**Trigger:** Gemini analyzes logs and returns a **High Confidence (>0.8)** suggestion.

1.  **Override**: Even if the rule-based detector suggests escalation (Tier-1), the AI's high confidence overrides it.
2.  **Action**: The system executes the AI's plan (e.g., `scale_deployment`, `restart_pod`).
3.  **Benefit**: Handles complex "gray area" incidents automatically.

### Supported Actions
The system currently supports:
*   `restart_pod`: Deletes the pod to force a restart.
*   `scale_deployment`: Updates the replica count of a deployment.

---

## 3. Real-World Setup Requirements

To use this in production, you must configure the `.env` file with real credentials:

### Kubernetes Access
The application needs access to your K8s cluster.
*   **In-Cluster**: If deployed inside K8s, it uses the ServiceAccount token automatically.
*   **External**: Ensure your `~/.kube/config` is valid and accessible, or set `KUBECONFIG` environment variable.

### ServiceNow Integration
Required variables in `.env`:
*   `SNOW_URL`: Your instance URL (e.g., `https://dev12345.service-now.com`).
*   `SNOW_USER`: Service account username.
*   `SNOW_PASS`: Service account password.

### Slack Integration
Required variables in `.env`:
*   `SLACK_BOT_TOKEN`: Bot User OAuth Token (starts with `xoxb-`).
*   `SLACK_CHANNEL`: Channel ID or name (e.g., `#ops-alerts`).

### Gemini (AI Insights)
Required variable in `.env`:
*   `GEMINI_API_KEY`: API key from Google AI Studio.
    *   *Usage*: The system sends logs to Gemini to analyze root causes and suggest fixes if the rule-based detector is unsure.
