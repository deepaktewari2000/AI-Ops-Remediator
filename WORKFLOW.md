# AI-Ops-Remediator Workflow

This document outlines the complete end-to-end flow of the system, including the new **Active Monitoring** and **AI Insights** capabilities.

## High-Level Flow

```mermaid
graph TD
    A[Start] --> B{Source?}
    B -- Active Monitor --> C[Poll K8s Logs]
    B -- Webhook --> D[Receive Alert]
    
    C --> E{Error Found?}
    E -- No --> C
    E -- Yes --> F[Create Incident]
    
    D --> F
    
    F --> G[Fetch Recent Logs]
    G --> H[GenAI Analysis]
    H --> I[Detector Evaluate]
    
    H --> I[Detector Evaluate]
    
    I --> J{AI Confidence > 0.8?}
    J -- Yes --> K[Auto-Remediate (Scale/Restart)]
    J -- No --> L{Severity?}
    
    L -- Tier-3 (Critical) --> K
    L -- Tier-1/2 (Warning) --> M[Escalate]
    
    K --> N{Success?}
    N -- Yes --> O[Resolve & Log]
    N -- No --> M
    
    M --> P[Slack Notification]
    M --> Q[ServiceNow Ticket]
```

## Detailed Steps

### 1. Detection (Two Modes)
*   **Reactive (Webhook)**: External tools (Prometheus, Datadog) send a POST request to `/api/v1/incidents/`.
*   **Proactive (Polling)**: The `LogMonitor` runs every 60s, scanning all pods for keywords like "Error" or "Exception".

### 2. Enrichment
*   **Log Retrieval**: The system connects to the specific pod and fetches the last 50 lines of logs (configurable).
*   **AI Analysis**: Google Gemini analyzes these logs to identify the *root cause* and suggest *remediation actions*.

### 3. Decision (Detector + AI)
*   The `Detector` evaluates the incident severity.
*   **AI Override**: If Gemini provides a solution with **Confidence > 0.8**, the system *bypasses* the manual escalation path and auto-remediates immediately.
*   **Tier-3**: Critical issues with a clear fix.
*   **Tier-1/2**: Complex or warning-level issues requiring human eyes (unless overridden by AI).

### 4. Execution
*   **Auto-Remediation**: The `Remediator` executes actions:
    *   `restart_pod`: For crashes/OOM.
    *   `scale_deployment`: For high load/traffic.
*   **Escalation**: If remediation fails or isn't allowed, the `Notifier` sends a Slack alert and creates a ServiceNow ticket containing the **AI analysis**.
