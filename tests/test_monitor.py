import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.monitor import LogMonitor

@pytest.mark.asyncio
async def test_monitor_scan_pods():
    mock_orch = AsyncMock()
    monitor = LogMonitor(mock_orch, interval=1)
    
    # Mock Kubernetes API
    monitor.api = MagicMock()
    
    # Mock list_namespaced_pod
    mock_pod = MagicMock()
    mock_pod.metadata.name = "test-pod"
    monitor.api.list_namespaced_pod.return_value.items = [mock_pod]
    
    # Mock read_namespaced_pod_log
    monitor.api.read_namespaced_pod_log.return_value = "Some normal log\nError: Something crashed\nMore logs"
    
    # Run scan
    await monitor._scan_pods()
    
    # Verify incident was created
    mock_orch.process_incident.assert_called_once()
    call_args = mock_orch.process_incident.call_args[0][0]
    assert call_args["source"] == "LogMonitor"
    assert call_args["severity"] == "critical"
    assert call_args["details"]["pod"] == "test-pod"

@pytest.mark.asyncio
async def test_monitor_no_error():
    mock_orch = AsyncMock()
    monitor = LogMonitor(mock_orch, interval=1)
    monitor.api = MagicMock()
    
    mock_pod = MagicMock()
    mock_pod.metadata.name = "healthy-pod"
    monitor.api.list_namespaced_pod.return_value.items = [mock_pod]
    monitor.api.read_namespaced_pod_log.return_value = "Just info logs\nNothing to see here"
    
    await monitor._scan_pods()
    
    mock_orch.process_incident.assert_not_called()
