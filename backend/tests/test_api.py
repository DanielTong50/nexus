"""Tests for API routes including chat streaming and approvals.

Tests verify:
- /chat endpoint processes requests and returns results
- /chat/stream endpoint streams SSE events
- /approve endpoint handles approvals/rejections
- /approvals endpoint lists pending approvals
"""

import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from src.main import app
from src.api.streaming import PENDING_APPROVALS, create_stream_event
from src.models.requests import PendingApproval, StreamEvent


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def clear_approvals():
    """Clear pending approvals before/after test."""
    PENDING_APPROVALS.clear()
    yield
    PENDING_APPROVALS.clear()


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_health_check(self, client):
        """Health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_agents_health(self, client):
        """Agents health endpoint returns agent status."""
        response = client.get("/api/health/agents")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["count"] == 5


class TestChatEndpoint:
    """Tests for synchronous chat endpoint."""

    @pytest.fixture
    def mock_classify(self):
        """Mock the classifier."""
        with patch("src.api.routes.classify_request") as mock:
            async def side_effect(state):
                return {"target_agents": ["partnerships", "finance"]}
            mock.side_effect = side_effect
            yield mock

    @pytest.fixture
    def mock_agents(self):
        """Mock agent execution."""
        with patch("src.api.routes.run_agents_parallel") as mock:
            async def side_effect(state):
                from src.models.state import AgentResult
                return {
                    "agent_results": [
                        AgentResult(
                            agent_name="partnerships",
                            status="success",
                            message="Done",
                        ),
                        AgentResult(
                            agent_name="finance",
                            status="success",
                            message="Done",
                        ),
                    ],
                    "completed_agents": ["partnerships", "finance"],
                }
            mock.side_effect = side_effect
            yield mock

    def test_chat_returns_response(self, client, mock_classify, mock_agents):
        """Chat endpoint returns proper response."""
        response = client.post(
            "/api/chat",
            json={"message": "Update sponsor status for Google"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "request_id" in data
        assert data["message"] == "Update sponsor status for Google"
        assert len(data["agents_invoked"]) == 2

    def test_chat_with_no_agents(self, client):
        """Chat returns empty results when no agents needed."""
        with patch("src.api.routes.classify_request") as mock:
            async def side_effect(state):
                return {"target_agents": []}
            mock.side_effect = side_effect

            response = client.post(
                "/api/chat",
                json={"message": "Hello"},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["agents_invoked"] == []
            assert data["results"] == []


class TestChatStreamEndpoint:
    """Tests for SSE streaming chat endpoint."""

    def test_stream_returns_sse_response(self, client):
        """Stream endpoint returns SSE content type."""
        with patch("src.api.streaming.classify_request") as mock_classify:
            async def classify_side_effect(state):
                return {"target_agents": []}
            mock_classify.side_effect = classify_side_effect

            response = client.post(
                "/api/chat/stream",
                json={"message": "Test message"},
            )

            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")

    def test_stream_get_endpoint(self, client):
        """GET stream endpoint works for EventSource compatibility."""
        with patch("src.api.streaming.classify_request") as mock_classify:
            async def classify_side_effect(state):
                return {"target_agents": []}
            mock_classify.side_effect = classify_side_effect

            response = client.get(
                "/api/chat/stream?message=Test%20message",
            )

            assert response.status_code == 200


class TestCreateStreamEvent:
    """Tests for stream event creation."""

    def test_creates_valid_json(self):
        """create_stream_event returns valid JSON."""
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
        event = create_stream_event("complete", {"done": True})
        data = json.loads(event)
        assert "timestamp" in data


class TestApprovalEndpoints:
    """Tests for approval-related endpoints."""

    def test_list_approvals_empty(self, client, clear_approvals):
        """List approvals returns empty list when none pending."""
        response = client.get("/api/approvals")

        assert response.status_code == 200
        data = response.json()
        assert data["pending"] == []
        assert data["count"] == 0

    def test_list_approvals_with_pending(self, client, clear_approvals):
        """List approvals returns pending items."""
        # Add a pending approval
        approval = PendingApproval(
            approval_id="test-123",
            request_id="req-1",
            agent_name="finance",
            action_type="draft_mou",
            action_description="Draft MOU for Google",
            action_data={"sponsor": "Google", "amount": 1000},
        )
        PENDING_APPROVALS["test-123"] = approval

        response = client.get("/api/approvals")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["pending"][0]["approval_id"] == "test-123"

    def test_get_approval_by_id(self, client, clear_approvals):
        """Get specific approval by ID."""
        approval = PendingApproval(
            approval_id="test-456",
            request_id="req-2",
            agent_name="marketing",
            action_type="schedule_instagram_post",
            action_description="Schedule post",
            action_data={"content": "Test post"},
        )
        PENDING_APPROVALS["test-456"] = approval

        response = client.get("/api/approvals/test-456")

        assert response.status_code == 200
        data = response.json()
        assert data["approval_id"] == "test-456"
        assert data["agent_name"] == "marketing"

    def test_get_approval_not_found(self, client, clear_approvals):
        """Get approval returns 404 for non-existent ID."""
        response = client.get("/api/approvals/nonexistent")
        assert response.status_code == 404

    def test_approve_action(self, client, clear_approvals):
        """Approve action successfully."""
        approval = PendingApproval(
            approval_id="approve-test",
            request_id="req-3",
            agent_name="finance",
            action_type="generate_invoice",
            action_description="Generate invoice for Google",
            action_data={"sponsor": "Google", "amount": 1000},
        )
        PENDING_APPROVALS["approve-test"] = approval

        response = client.post(
            "/api/approve",
            json={
                "approval_id": "approve-test",
                "action": "approve",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "executed"
        assert "approve-test" in data["approval_id"]

    def test_reject_action(self, client, clear_approvals):
        """Reject action successfully."""
        approval = PendingApproval(
            approval_id="reject-test",
            request_id="req-4",
            agent_name="events",
            action_type="announce_to_slack",
            action_description="Post to Slack",
            action_data={"message": "Test"},
        )
        PENDING_APPROVALS["reject-test"] = approval

        response = client.post(
            "/api/approve",
            json={
                "approval_id": "reject-test",
                "action": "reject",
                "reason": "Not ready yet",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"
        assert "Not ready yet" in data["message"]

    def test_edit_and_approve(self, client, clear_approvals):
        """Edit action data and approve."""
        approval = PendingApproval(
            approval_id="edit-test",
            request_id="req-5",
            agent_name="finance",
            action_type="draft_mou",
            action_description="Draft MOU",
            action_data={"amount": 1000},
        )
        PENDING_APPROVALS["edit-test"] = approval

        response = client.post(
            "/api/approve",
            json={
                "approval_id": "edit-test",
                "action": "edit",
                "edits": {"amount": 1500},
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "executed"
        assert data["result"]["edits_applied"]["amount"] == 1500

    def test_approve_not_found(self, client, clear_approvals):
        """Approve returns 404 for non-existent approval."""
        response = client.post(
            "/api/approve",
            json={
                "approval_id": "nonexistent",
                "action": "approve",
            },
        )

        assert response.status_code == 404

    def test_approve_already_processed(self, client, clear_approvals):
        """Cannot approve already processed approval."""
        approval = PendingApproval(
            approval_id="already-done",
            request_id="req-6",
            agent_name="finance",
            action_type="draft_mou",
            action_description="Already done",
            action_data={},
            status="approved",
        )
        PENDING_APPROVALS["already-done"] = approval

        response = client.post(
            "/api/approve",
            json={
                "approval_id": "already-done",
                "action": "approve",
            },
        )

        assert response.status_code == 400

    def test_cancel_approval(self, client, clear_approvals):
        """Cancel/delete pending approval."""
        approval = PendingApproval(
            approval_id="cancel-test",
            request_id="req-7",
            agent_name="marketing",
            action_type="schedule_linkedin_post",
            action_description="Test",
            action_data={},
        )
        PENDING_APPROVALS["cancel-test"] = approval

        response = client.delete("/api/approvals/cancel-test")

        assert response.status_code == 200
        assert "cancel-test" not in PENDING_APPROVALS


class TestAgentsEndpoint:
    """Tests for agents info endpoint."""

    def test_list_agents(self, client):
        """List agents returns all 5 agents."""
        response = client.get("/api/agents")

        assert response.status_code == 200
        data = response.json()
        assert len(data["agents"]) == 5

        agent_names = [a["name"] for a in data["agents"]]
        assert "partnerships" in agent_names
        assert "marketing" in agent_names
        assert "finance" in agent_names
        assert "events" in agent_names
        assert "developers" in agent_names

    def test_agents_have_tools(self, client):
        """Each agent has tools defined."""
        response = client.get("/api/agents")
        data = response.json()

        for agent in data["agents"]:
            assert "tools" in agent
            assert len(agent["tools"]) > 0
