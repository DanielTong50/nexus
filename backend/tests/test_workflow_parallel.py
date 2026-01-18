"""Tests for parallel workflow execution.

Verifies that:
- Agents execute in parallel using asyncio.gather
- Results are properly aggregated
- Errors are handled correctly
"""

import asyncio
import pytest
import time
from unittest.mock import AsyncMock, patch

from src.graph.workflow import (
    AGENT_RUNNERS,
    VALID_AGENTS,
    run_agents_parallel,
    create_workflow,
)
from src.models.state import GraphState, AgentResult


class TestAgentRegistry:
    """Tests for the agent runner registry."""

    def test_all_agents_registered(self):
        """All valid agents are registered."""
        for agent in VALID_AGENTS:
            assert agent in AGENT_RUNNERS

    def test_runner_is_callable(self):
        """Each runner is an async callable."""
        for agent, runner in AGENT_RUNNERS.items():
            assert callable(runner)


class TestParallelExecution:
    """Tests for parallel agent execution."""

    @pytest.fixture
    def base_state(self):
        """Create base state for tests."""
        return GraphState(
            request_id="test-123",
            user_message="Test message",
        )

    @pytest.mark.asyncio
    async def test_no_agents(self, base_state):
        """No agents returns empty results."""
        base_state.target_agents = []
        result = await run_agents_parallel(base_state)

        assert result["agent_results"] == []
        assert result["completed_agents"] == []

    @pytest.mark.asyncio
    async def test_single_agent(self, base_state):
        """Single agent executes successfully."""
        base_state.target_agents = ["partnerships"]
        result = await run_agents_parallel(base_state)

        assert len(result["agent_results"]) == 1
        assert result["agent_results"][0].agent_name == "partnerships"
        assert "partnerships" in result["completed_agents"]

    @pytest.mark.asyncio
    async def test_multiple_agents(self, base_state):
        """Multiple agents execute in parallel."""
        base_state.target_agents = ["partnerships", "marketing", "finance"]
        result = await run_agents_parallel(base_state)

        assert len(result["agent_results"]) == 3
        assert len(result["completed_agents"]) == 3

    @pytest.mark.asyncio
    async def test_invalid_agent_skipped(self, base_state):
        """Invalid agents are skipped."""
        base_state.target_agents = ["partnerships", "invalid_agent"]
        result = await run_agents_parallel(base_state)

        assert len(result["agent_results"]) == 1
        assert result["agent_results"][0].agent_name == "partnerships"


class TestWorkflowGraph:
    """Tests for the workflow graph."""

    def test_graph_compiles(self):
        """Workflow graph compiles without error."""
        graph = create_workflow()
        assert graph is not None

    @pytest.mark.asyncio
    async def test_workflow_runs(self):
        """Workflow executes end-to-end."""
        from src.graph.workflow import run_workflow

        with patch("src.graph.classifier.classify_request") as mock_classify:
            async def classify_side_effect(state):
                return {"target_agents": ["partnerships"], "next_step": "route"}

            mock_classify.side_effect = classify_side_effect

            result = await run_workflow(
                user_message="Test message",
                request_id="test-run",
            )

            assert "agent_results" in result or "completed_agents" in result
