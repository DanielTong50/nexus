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
from src.api.streaming import create_stream_event
from src.models.requests import PendingApproval, StreamEvent
from src.models.approval import ApprovalDocument


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_approval_repo():
    """Mock the approval repository for tests."""
    with patch("src.api.streaming._get_approval_repo") as mock_get_repo, \
         patch("src.api.routes.get_pending_approval") as mock_get, \
         patch("src.api.routes.get_all_pending_approvals") as mock_get_all, \
         patch("src.api.routes.update_approval_status") as mock_update, \
         patch("src.api.routes.delete_approval") as mock_delete:

        # Storage for mock approvals
        mock_approvals = {}

        async def get_approval(approval_id):
            return mock_approvals.get(approval_id)

        async def get_all_approvals():
            return [a for a in mock_approvals.values() if a.status == "pending"]

        async def update_status(approval_id, status, **kwargs):
            if approval_id in mock_approvals:
                mock_approvals[approval_id].status = status
                return mock_approvals[approval_id]
            return None

        async def delete(approval_id):
            if approval_id in mock_approvals:
                del mock_approvals[approval_id]
                return True
            return False

        mock_get.side_effect = get_approval
        mock_get_all.side_effect = get_all_approvals
        mock_update.side_effect = update_status
        mock_delete.side_effect = delete

        yield mock_approvals


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_health_check(self, client):
        """Health endpoint returns healthy status."""
        response = client.get("/api/health")
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

    def test_list_approvals_empty(self, client, mock_approval_repo):
        """List approvals returns empty list when none pending."""
        response = client.get("/api/approvals")

        assert response.status_code == 200
        data = response.json()
        assert data["pending"] == []
        assert data["count"] == 0

    def test_list_approvals_with_pending(self, client, mock_approval_repo):
        """List approvals returns pending items."""
        # Add a pending approval
        approval = ApprovalDocument(
            approval_id="test-123",
            request_id="req-1",
            agent_name="finance",
            action_type="draft_mou",
            action_description="Draft MOU for Google",
            action_data={"sponsor": "Google", "amount": 1000},
        )
        mock_approval_repo["test-123"] = approval

        response = client.get("/api/approvals")

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["pending"][0]["approval_id"] == "test-123"

    def test_get_approval_by_id(self, client, mock_approval_repo):
        """Get specific approval by ID."""
        approval = ApprovalDocument(
            approval_id="test-456",
            request_id="req-2",
            agent_name="marketing",
            action_type="schedule_instagram_post",
            action_description="Schedule post",
            action_data={"content": "Test post"},
        )
        mock_approval_repo["test-456"] = approval

        response = client.get("/api/approvals/test-456")

        assert response.status_code == 200
        data = response.json()
        assert data["approval_id"] == "test-456"
        assert data["agent_name"] == "marketing"

    def test_get_approval_not_found(self, client, mock_approval_repo):
        """Get approval returns 404 for non-existent ID."""
        response = client.get("/api/approvals/nonexistent")
        assert response.status_code == 404

    def test_approve_action(self, client, mock_approval_repo):
        """Approve action successfully."""
        approval = ApprovalDocument(
            approval_id="approve-test",
            request_id="req-3",
            agent_name="finance",
            action_type="generate_invoice",
            action_description="Generate invoice for Google",
            action_data={"sponsor": "Google", "amount": 1000},
        )
        mock_approval_repo["approve-test"] = approval

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

    def test_reject_action(self, client, mock_approval_repo):
        """Reject action successfully."""
        approval = ApprovalDocument(
            approval_id="reject-test",
            request_id="req-4",
            agent_name="events",
            action_type="announce_to_slack",
            action_description="Post to Slack",
            action_data={"message": "Test"},
        )
        mock_approval_repo["reject-test"] = approval

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

    def test_edit_and_approve(self, client, mock_approval_repo):
        """Edit action data and approve."""
        approval = ApprovalDocument(
            approval_id="edit-test",
            request_id="req-5",
            agent_name="finance",
            action_type="draft_mou",
            action_description="Draft MOU",
            action_data={"amount": 1000},
        )
        mock_approval_repo["edit-test"] = approval

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

    def test_approve_not_found(self, client, mock_approval_repo):
        """Approve returns 404 for non-existent approval."""
        response = client.post(
            "/api/approve",
            json={
                "approval_id": "nonexistent",
                "action": "approve",
            },
        )

        assert response.status_code == 404

    def test_approve_already_processed(self, client, mock_approval_repo):
        """Cannot approve already processed approval."""
        approval = ApprovalDocument(
            approval_id="already-done",
            request_id="req-6",
            agent_name="finance",
            action_type="draft_mou",
            action_description="Already done",
            action_data={},
            status="approved",
        )
        mock_approval_repo["already-done"] = approval

        response = client.post(
            "/api/approve",
            json={
                "approval_id": "already-done",
                "action": "approve",
            },
        )

        assert response.status_code == 400

    def test_cancel_approval(self, client, mock_approval_repo):
        """Cancel/delete pending approval."""
        approval = ApprovalDocument(
            approval_id="cancel-test",
            request_id="req-7",
            agent_name="marketing",
            action_type="schedule_linkedin_post",
            action_description="Test",
            action_data={},
        )
        mock_approval_repo["cancel-test"] = approval

        response = client.delete("/api/approvals/cancel-test")

        assert response.status_code == 200
        assert "cancel-test" not in mock_approval_repo


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
