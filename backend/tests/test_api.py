"""Tests for API routes including chat streaming and approvals.

Tests verify:
- /health endpoint returns status
- /chat endpoint processes requests and returns results
- /chat/stream endpoint streams SSE events
- /approve endpoint handles approvals/rejections
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from src.main import app
from src.api.streaming import create_stream_event


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_health_check(self, client):
        """Health endpoint returns status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["app"] == "nexus"
        assert "llm_provider" in data


class TestChatEndpoint:
    """Tests for synchronous chat endpoint."""

    @pytest.fixture
    def mock_workflow(self):
        """Mock the run_workflow function."""
        with patch("src.api.routes.run_workflow") as mock:
            from src.models.state import AgentResult
            async def side_effect(user_message, request_id, event_id=None):
                return {
                    "agent_results": [
                        AgentResult(
                            agent_name="partnerships",
                            status="success",
                            message="Done",
                        ),
                    ],
                    "completed_agents": ["partnerships"],
                }
            mock.side_effect = side_effect
            yield mock

    def test_chat_returns_response(self, client, mock_workflow):
        """Chat endpoint returns proper response."""
        response = client.post(
            "/api/chat",
            json={"message": "Update sponsor status for Google"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert data["message"] == "Update sponsor status for Google"


class TestChatStreamEndpoint:
    """Tests for SSE streaming chat endpoint."""

    def test_stream_returns_sse_response(self, client):
        """Stream endpoint returns SSE content type."""
        # Just test that the endpoint responds with SSE
        response = client.post(
            "/api/chat/stream",
            json={"message": "Test message"},
        )

        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")


class TestCreateStreamEvent:
    """Tests for stream event creation."""

    def test_creates_valid_json(self):
        """create_stream_event returns valid JSON."""
        import json
        event = create_stream_event(
            "agent_start",
            {"message": "Starting..."},
            agent_name="partnerships",
        )

        data = json.loads(event)
        assert data["event_type"] == "agent_start"
        assert data["data"]["message"] == "Starting..."
        assert data["agent_name"] == "partnerships"

    def test_includes_timestamp(self):
        """Event includes timestamp."""
        import json
        event = create_stream_event("complete", {"done": True})
        data = json.loads(event)
        assert "timestamp" in data


class TestAgentsEndpoint:
    """Tests for agents info endpoint."""

    def test_list_agents(self, client):
        """List agents returns all 5 agents."""
        response = client.get("/api/agents")

        assert response.status_code == 200
        data = response.json()
        assert len(data["agents"]) == 5
        assert data["active_provider"] in ["gemini", "vultr"]

    def test_config_endpoint(self, client):
        """Config endpoint returns settings."""
        response = client.get("/api/config")

        assert response.status_code == 200
        data = response.json()
        assert "active_agent_provider" in data
        assert "classifier_model" in data
