# AI-Ops-Remediator

**Self-healing microservice platform** — Python · FastAPI · Docker · Kubernetes · Slack · ServiceNow · GenAI

AI-Ops-Remediator is an autonomous system that detects, analyzes, and fixes infrastructure failures in real-time. It combines active monitoring with Generative AI to resolve incidents before they require human intervention.

---

## 🚀 Key Features

*   **Active Monitoring**: Proactively polls Kubernetes logs (every 60s) to detect errors immediately.
*   **AI-First Resolution**: Uses **Google Gemini** to analyze logs. If the AI is highly confident (>0.8), it **automatically executes** the fix.
*   **Auto-Remediation**:
    *   **Restart Pods**: For OOM kills, deadlocks, or crashes.
    *   **Scale Deployments**: For high CPU/memory load.
*   **Smart Escalation**: If the AI is unsure, it creates a **ServiceNow ticket** and sends a **Slack alert** with the AI's full root-cause analysis attached.
*   **Dry-Run Mode**: Safe to run locally; simulates actions without touching the cluster if no K8s config is found.

---

## 🔄 Workflow

```mermaid
graph TD
    A[Start] --> B{Source?}
    B -- Active Monitor --> C[Poll K8s Logs]
    B -- Webhook --> D[Receive Alert]
    
    C --> E{Error Found?}
    E -- Yes --> F[Create Incident]
    
    D --> F
    
    F --> G[Fetch Recent Logs]
    G --> H[GenAI Analysis]
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

---

## 🛠️ Quick Start

### Prerequisites
*   Python 3.11+
*   Docker & Kubernetes (optional, for full features)

### 1. Setup
```bash
git clone <repo-url>
cd AI-Ops-Remediator
pip install -r requirements.txt
```

### 2. Configure
Copy `.env.example` to `.env` and set your keys:
```bash
cp .env.example .env
# Edit .env: GEMINI_API_KEY, SLACK_BOT_TOKEN, SNOW_URL, etc.
```

### 3. Run
```bash
uvicorn app.main:app --reload
```
*The system will start monitoring logs immediately.*

---

## 📚 Documentation

*   **[Running Guide](RUNNING.md)**: Detailed setup and installation instructions.
*   **[User Guide](USER_GUIDE.md)**: Real-world scenarios, integration details, and supported actions.
*   **[Workflow](WORKFLOW.md)**: Deep dive into the decision logic and architecture.

---

## 🧪 Testing

Run the test suite to verify logic:
```bash
pytest
```
