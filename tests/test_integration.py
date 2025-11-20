import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_dependencies():
    with patch("app.core.dependencies.orchestrator") as mock_orch:
        mock_orch.process_incident = AsyncMock()
        yield mock_orch

def test_create_incident(mock_dependencies):
    payload = {
        "source": "test-service",
        "severity": "critical",
        "details": {"msg": "something bad"}
    }
    response = client.post("/api/v1/incidents/", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "incident received"}
    # Verify orchestrator was called in background
    # Note: BackgroundTasks are hard to test synchronously with TestClient unless we force execution.
    # However, we can verify the endpoint returned success.

@pytest.mark.asyncio
async def test_orchestrator_flow_tier_3():
    # Test the logic inside Orchestrator without real dependencies
    from app.core.orchestrator import Orchestrator
    
    with patch("app.core.orchestrator.Detector") as MockDetector, \
         patch("app.core.orchestrator.Remediator") as MockRemediator, \
         patch("app.core.orchestrator.Notifier") as MockNotifier:
        
        # Setup mocks
        mock_detector = MockDetector.return_value
        mock_remediator = MockRemediator.return_value
        mock_notifier = MockNotifier.return_value
        
        # Tier-3 scenario
        mock_detector.evaluate.return_value = ("tier-3", {"actions": [{"type": "restart"}]})
        mock_remediator.execute = AsyncMock(return_value={"success": True})
        mock_remediator.get_pod_logs.return_value = "Error: OOMKilled"
        
        orch = Orchestrator()
        result = await orch.process_incident({"severity": "critical", "details": {"pod": "test-pod"}})
        
        assert result["action"] == "auto_remediated"
        mock_remediator.execute.assert_called_once()
        mock_remediator.get_pod_logs.assert_called_once()
        # We can't easily verify GenAI call here without mocking sys.modules or using more complex patching
        # because the import happens inside the method. 
        # But we can verify the logic flow attempted to get logs.

@pytest.mark.asyncio
async def test_orchestrator_flow_tier_1():
    from app.core.orchestrator import Orchestrator
    
    with patch("app.core.orchestrator.Detector") as MockDetector, \
         patch("app.core.orchestrator.Remediator") as MockRemediator, \
         patch("app.core.orchestrator.Notifier") as MockNotifier:
        
        mock_detector = MockDetector.return_value
        mock_notifier = MockNotifier.return_value
        
        # Tier-1 scenario
        mock_detector.evaluate.return_value = ("tier-1-2", {})
        mock_notifier.escalate.return_value = "INC123"
        
        orch = Orchestrator()
        result = await orch.process_incident({"severity": "warning"})
        
        assert result["action"] == "escalated"
        assert result["ticket"] == "INC123"
        mock_notifier.escalate.assert_called_once()

@pytest.mark.asyncio
async def test_orchestrator_ai_override():
    from app.core.orchestrator import Orchestrator
    
    with patch("app.core.orchestrator.Detector") as MockDetector, \
         patch("app.core.orchestrator.Remediator") as MockRemediator, \
         patch("app.core.orchestrator.Notifier") as MockNotifier, \
         patch("app.core.insights.GenAIInsights") as MockInsights:
        
        mock_detector = MockDetector.return_value
        mock_remediator = MockRemediator.return_value
        mock_insights = MockInsights.return_value
        
        # Scenario: Detector says Tier-1 (escalate), but AI says Scale (Confidence 0.9)
        mock_detector.evaluate.return_value = ("tier-1-2", {})
        
        # Mock AI analysis
        mock_insights.analyze.return_value = {
            "root_cause": "High CPU",
            "suggested_actions": [{"type": "scale", "deployment_name": "web", "value": 3}],
            "confidence": 0.9
        }
        
        mock_remediator.execute = AsyncMock(return_value={"success": True})
        mock_remediator.get_pod_logs.return_value = "High CPU usage detected"
        
        orch = Orchestrator()
        # We need to ensure GenAIInsights is instantiated inside process_incident
        # The patch above mocks the class, so orch.process_incident will use the mock
        
        result = await orch.process_incident({"severity": "warning", "details": {"pod": "web-1"}})
        
        # Expectation: Auto-remediated because AI confidence > 0.8
        assert result["action"] == "auto_remediated"
        mock_remediator.execute.assert_called_once()
        
        # Verify the plan passed to execute
        plan = mock_remediator.execute.call_args[0][0]
        assert plan["actions"][0]["type"] == "scale"
        assert plan["actions"][0]["value"] == 3
