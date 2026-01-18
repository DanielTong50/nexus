"""Tests for the router node.

Tests verify that the router correctly creates agent assignments
and routes to appropriate agents.
"""

import pytest
from unittest.mock import AsyncMock, patch

from src.graph.router import (
    VALID_AGENTS,
    AgentAssignment,
    RouterOutput,
    create_agent_assignments,
    get_agent_sub_prompt,
    get_all_target_agents,
    should_run_agent,
    router_node,
)
from src.models.state import GraphState


class TestValidAgents:
    """Tests for valid agent list."""

    def test_all_agents_present(self):
        """All expected agents are present."""
        expected = {"partnerships", "marketing", "finance", "events", "developers"}
        assert VALID_AGENTS == expected


class TestAgentSubPrompt:
    """Tests for sub-prompt generation."""

    def test_returns_user_message(self):
        """Currently returns the full user message."""
        message = "Test message"
        result = get_agent_sub_prompt("partnerships", message)
        assert result == message


class TestCreateAgentAssignments:
    """Tests for creating agent assignments."""

    def test_creates_assignments_for_valid_agents(self):
        """Create assignments for valid agents."""
        assignments = create_agent_assignments(
            target_agents=["partnerships", "finance"],
            user_message="Test message",
        )
        assert len(assignments) == 2
        assert all(isinstance(a, AgentAssignment) for a in assignments)

    def test_skips_invalid_agents(self):
        """Skip invalid agent names."""
        assignments = create_agent_assignments(
            target_agents=["partnerships", "invalid", "marketing"],
            user_message="Test message",
        )
        assert len(assignments) == 2
        names = [a.agent_name for a in assignments]
        assert "invalid" not in names

    def test_empty_target_agents(self):
        """Empty target list returns empty assignments."""
        assignments = create_agent_assignments(
            target_agents=[],
            user_message="Test message",
        )
        assert len(assignments) == 0


class TestRouterNode:
    """Tests for the router node function."""

    @pytest.fixture
    def base_state(self):
        """Create base state for tests."""
        return GraphState(
            request_id="test-123",
            user_message="Test message",
        )

    @pytest.mark.asyncio
    async def test_creates_router_output(self, base_state):
        """Router node creates RouterOutput."""
        base_state.target_agents = ["partnerships", "marketing"]
        result = await router_node(base_state)

        assert "router_output" in result
        assert isinstance(result["router_output"], RouterOutput)

    @pytest.mark.asyncio
    async def test_parallel_execution_flag(self, base_state):
        """Sets parallel flag when multiple agents."""
        base_state.target_agents = ["partnerships", "marketing"]
        result = await router_node(base_state)

        assert result["router_output"].should_execute_parallel is True

    @pytest.mark.asyncio
    async def test_single_agent_not_parallel(self, base_state):
        """Single agent does not set parallel flag."""
        base_state.target_agents = ["partnerships"]
        result = await router_node(base_state)

        assert result["router_output"].should_execute_parallel is False


class TestHelperFunctions:
    """Tests for helper functions."""

    @pytest.fixture
    def base_state(self):
        """Create base state for tests."""
        return GraphState(
            request_id="test-123",
            user_message="Test message",
            target_agents=["partnerships", "marketing"],
        )

    def test_get_all_target_agents(self, base_state):
        """Get all valid target agents from state."""
        result = get_all_target_agents(base_state)
        assert result == ["partnerships", "marketing"]

    def test_get_all_target_agents_filters_invalid(self, base_state):
        """Filters out invalid agents."""
        base_state.target_agents = ["partnerships", "invalid", "marketing"]
        result = get_all_target_agents(base_state)
        assert result == ["partnerships", "marketing"]

    def test_should_run_agent_returns_true(self, base_state):
        """Returns true for valid target agent."""
        assert should_run_agent(base_state, "partnerships") is True

    def test_should_run_agent_returns_false(self, base_state):
        """Returns false for non-target agent."""
        assert should_run_agent(base_state, "developers") is False
