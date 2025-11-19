import os
from slack_sdk import WebClient
import requests

class Notifier:
    def __init__(self):
        self.slack_token = os.getenv("SLACK_BOT_TOKEN")
        self.slack_channel = os.getenv("SLACK_CHANNEL", "#ops")
        if self.slack_token:
            self.slack = WebClient(token=self.slack_token)
        else:
            self.slack = None
        self.snow_url = os.getenv("SNOW_URL")
        self.snow_user = os.getenv("SNOW_USER")
        self.snow_pass = os.getenv("SNOW_PASS")

    def post_slack(self, message: str, blocks=None):
        if not self.slack:
            print("[slack]", message)
            return {"ok": False, "reason": "no-token"}
        return self.slack.chat_postMessage(channel=self.slack_channel, text=message, blocks=blocks)

    def create_servicenow_ticket(self, short_desc: str, details: dict):
        if not (self.snow_url and self.snow_user and self.snow_pass):
            return {"error": "servicenow not configured"}
        url = f"{self.snow_url}/api/now/table/incident"
        payload = {"short_description": short_desc, "description": str(details), "urgency": "2"}
        resp = requests.post(url, auth=(self.snow_user, self.snow_pass), json=payload, timeout=10)
        return resp.json() if resp.ok else {"error": resp.text}

    def escalate(self, incident, remediation_result):
        msg = f"Escalation: {incident.get('source')} - {incident.get('severity')}"
        self.post_slack(msg)
        ticket = self.create_servicenow_ticket(msg, {"incident": incident, "remediator": remediation_result})
        return ticket
