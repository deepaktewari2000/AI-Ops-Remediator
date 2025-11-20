import requests
import json

url = "http://localhost:8000/api/v1/incidents/"
headers = {"Content-Type": "application/json"}
data = {
    "source": "test",
    "severity": "critical",
    "details": {"msg": "oom"}
}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
