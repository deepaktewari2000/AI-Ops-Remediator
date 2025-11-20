import os
import google.generativeai as genai

class GenAIInsights:
    def __init__(self, api_key=None, model="gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model

        if not self.api_key:
            raise ValueError("Gemini API key missing. Set GEMINI_API_KEY env variable.")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def analyze(self, logs: str, context: dict):
        """
        Calls Gemini to analyze logs and return:
        - root_cause
        - suggested_actions
        - confidence (0–1)
        """

        prompt = f"""
You are an expert SRE/DevOps auto-remediation assistant embedded inside a self-healing
platform called AI-Ops-Remediator. You analyze logs and propose safe, JSON-only actions.

### LOGS
{logs}

### CONTEXT
{context}

### OUTPUT FORMAT (STRICT JSON)
{{
  "root_cause": "<root cause>",
  "suggested_actions": [
     {{
        "type": "<restart_pod | scale_deployment>",
        "namespace": "<k8s namespace>",
        "pod_name": "<pod name (for restart)>",
        "deployment_name": "<deployment name (for scale)>",
        "value": "<replicas (int) for scale>"
     }}
  ],
  "confidence": 0.0 to 1.0
}}

Rules:
- ONLY reply in JSON.
- If unsure, produce low confidence.
- Suggested actions must be safe, idempotent & minimal.
"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()

            # Ensure valid JSON output
            import json
            result = json.loads(text)
            return result

        except Exception as e:
            return {
                "root_cause": "analysis_failed",
                "suggested_actions": [],
                "confidence": 0.0,
                "error": str(e)
            }
