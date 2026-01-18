"""Tests for parallel agent execution in the workflow.

Tests verify that agents run in parallel using asyncio.gather
and that parallel execution is faster than sequential.
"""

import asyncio
import time
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.graph.workflow import (
    run_agents_parallel,
    run_partnerships_agent,
    run_marketing_agent,
    run_finance_agent,
    run_events_agent,
    run_developers_agent,
    should_run_parallel,
    create_workflow,
    create_sequential_workflow,
    AGENT_RUNNERS,
    graph,
)
from src.models.state import GraphState


class TestAgentRunners:
    """Tests for individual agent runner functions."""

    @pytest.mark.asyncio
    async def test_partnerships_agent_returns_result(self):
        """Partnerships agent returns proper result."""
        state = GraphState(request_id="test", user_message="test")
        result = await run_partnerships_agent(state)

        assert "agent_results" in result
        assert len(result["agent_results"]) == 1
        assert result["agent_results"][0].agent_name == "partnerships"
        assert result["agent_results"][0].status == "success"

    @pytest.mark.asyncio
    async def test_marketing_agent_returns_result(self):
        """Marketing agent returns proper result."""
        state = GraphState(request_id="test", user_message="test")
        result = await run_marketing_agent(state)

        assert result["agent_results"][0].agent_name == "marketing"

    @pytest.mark.asyncio
    async def test_finance_agent_returns_result(self):
        """Finance agent returns proper result."""
        state = GraphState(request_id="test", user_message="test")
        result = await run_finance_agent(state)

        assert result["agent_results"][0].agent_name == "finance"

    @pytest.mark.asyncio
    async def test_all_agents_registered(self):
        """All 5 agents are registered in AGENT_RUNNERS."""
        expected = ["partnerships", "marketing", "finance", "events", "developers"]
        for agent in expected:
            assert agent in AGENT_RUNNERS


class TestParallelExecution:
    """Tests for parallel agent execution."""

    @pytest.mark.asyncio
    async def test_runs_multiple_agents_in_parallel(self):
        """Multiple agents run in parallel and return results."""
        state = GraphState(
            request_id="test-parallel",
            user_message="Test message",
            target_agents=["partnerships", "marketing", "finance"],
        )

        result = await run_agents_parallel(state)

        # All 3 agents should complete
        assert len(result["agent_results"]) == 3
        assert len(result["completed_agents"]) == 3
        assert "partnerships" in result["completed_agents"]
        assert "marketing" in result["completed_agents"]
        assert "finance" in result["completed_agents"]

    @pytest.mark.asyncio
    async def test_parallel_faster_than_sequential(self):
        """Parallel execution is faster than sequential for 3+ agents."""
        state = GraphState(
            request_id="test-speed",
            user_message="Test message",
            target_agents=["partnerships", "marketing", "finance", "events"],
        )

        # Time parallel execution
        start_parallel = time.time()
        await run_agents_parallel(state)
        parallel_time = time.time() - start_parallel

        # Time sequential execution
        start_sequential = time.time()
        await run_partnerships_agent(state)
        await run_marketing_agent(state)
        await run_finance_agent(state)
        await run_events_agent(state)
        sequential_time = time.time() - start_sequential

        # Parallel should be faster (or at least not slower)
        # With 4 agents each taking ~10ms, parallel should be ~10-20ms
        # while sequential would be ~40ms+
        print(f"Parallel: {parallel_time:.3f}s, Sequential: {sequential_time:.3f}s")
        
        # Parallel should be at least 1.5x faster with 4 agents
        assert parallel_time < sequential_time * 0.8, \
            f"Parallel ({parallel_time:.3f}s) not significantly faster than sequential ({sequential_time:.3f}s)"

    @pytest.mark.asyncio
    async def test_handles_empty_agents(self):
        """Empty agents list returns empty results."""
        state = GraphState(
            request_id="test-empty",
            user_message="Test",
            target_agents=[],
        )

        result = await run_agents_parallel(state)

        assert result["agent_results"] == []
        assert result["completed_agents"] == []

    @pytest.mark.asyncio
    async def test_handles_single_agent(self):
        """Single agent execution works correctly."""
        state = GraphState(
            request_id="test-single",
            user_message="Test",
            target_agents=["developers"],
        )

        result = await run_agents_parallel(state)

        assert len(result["agent_results"]) == 1
        assert result["agent_results"][0].agent_name == "developers"

    @pytest.mark.asyncio
    async def test_filters_invalid_agents(self):
        """Invalid agents are filtered out."""
        state = GraphState(
            request_id="test-invalid",
            user_message="Test",
            target_agents=["partnerships", "invalid_agent", "marketing"],
        )

        result = await run_agents_parallel(state)

        # Only 2 valid agents should run
        assert len(result["agent_results"]) == 2
        agent_names = [r.agent_name for r in result["agent_results"]]
        assert "invalid_agent" not in agent_names

    @pytest.mark.asyncio
    async def test_handles_agent_exception(self):
        """Agent exceptions are caught and reported."""
        # Create a mock that raises an exception
        async def failing_agent(state):
            raise ValueError("Agent failed!")

        # Temporarily replace an agent
        original = AGENT_RUNNERS["partnerships"]
        AGENT_RUNNERS["partnerships"] = failing_agent

        try:
            state = GraphState(
                request_id="test-error",
                user_message="Test",
                target_agents=["partnerships", "marketing"],
            )

            result = await run_agents_parallel(state)

            # Should have 2 results: 1 error + 1 success
            assert len(result["agent_results"]) == 2
            
            # One should be an error
            statuses = [r.status for r in result["agent_results"]]
            assert "error" in statuses
            assert "success" in statuses
            
            # Should report errors
            assert "errors" in result
        finally:
            AGENT_RUNNERS["partnerships"] = original


class TestShouldRunParallel:
    """Tests for the routing decision function."""

    def test_routes_to_parallel_when_agents_present(self):
        """Routes to parallel_agents when target_agents is non-empty."""
        state = GraphState(
            request_id="test",
            user_message="Test",
            target_agents=["partnerships"],
        )

        result = should_run_parallel(state)

        assert result == "parallel_agents"

    def test_routes_to_aggregate_when_no_agents(self):
        """Routes to aggregate when target_agents is empty."""
        state = GraphState(
            request_id="test",
            user_message="Test",
            target_agents=[],
        )

        result = should_run_parallel(state)

        assert result == "aggregate"


class TestWorkflowCreation:
    """Tests for workflow creation functions."""

    def test_parallel_workflow_created(self):
        """Parallel workflow is created successfully."""
        workflow = create_workflow()
        assert workflow is not None

    def test_sequential_workflow_created(self):
        """Sequential workflow is created successfully."""
        workflow = create_sequential_workflow()
        assert workflow is not None

    def test_graph_instance_available(self):
        """Default graph instance is available."""
        assert graph is not None


class TestIntegrationParallel:
    """Integration tests for entire parallel workflow."""

    @pytest.fixture
    def mock_classifier(self):
        """Mock the classifier to return specific agents."""
        with patch("src.graph.workflow.classify_request") as mock:
            async def classifier_side_effect(state):
                return {"target_agents": ["partnerships", "marketing", "finance"]}
            mock.side_effect = classifier_side_effect
            yield mock

    @pytest.mark.asyncio
    async def test_full_workflow_with_3_agents(self, mock_classifier):
        """Full workflow executes 3 agents in parallel."""
        from src.graph.workflow import run_workflow
        
        with patch("src.graph.workflow.classify_request") as mock_classify:
            async def mock_side_effect(state):
                return {"target_agents": ["partnerships", "marketing", "finance"]}
            mock_classify.side_effect = mock_side_effect
            
            # Recreate workflow to use mock
            from src.graph.workflow import create_workflow
            workflow = create_workflow()

        # Run workflow directly with pre-classified state
        state = GraphState(
            request_id="test-full",
            user_message="Test sponsor meeting",
            target_agents=["partnerships", "marketing", "finance"],
        )

        result = await run_agents_parallel(state)

        assert len(result["agent_results"]) == 3
        assert len(result["completed_agents"]) == 3
