"""Tests for the router node.

Tests verify that the router correctly assigns prompts to agents
and supports parallel execution.
"""

import pytest

from src.graph.router import (
    route_to_agents,
    router_node,
    create_agent_assignments,
    get_agent_sub_prompt,
    get_all_target_agents,
    get_parallel_agent_nodes,
    should_run_agent,
    AgentAssignment,
    RouterOutput,
    VALID_AGENTS,
)
from src.models.state import GraphState


class TestRouteToAgents:
    """Tests for the main routing function."""

    def test_routes_to_first_agent(self):
        """Route to the first agent when multiple are specified."""
        state = GraphState(
            request_id="test-1",
            user_message="Test message",
            target_agents=["partnerships", "finance"],
        )
        
        result = route_to_agents(state)
        
        assert result == "partnerships"

    def test_routes_to_aggregate_when_no_agents(self):
        """Route to aggregate when no agents are specified."""
        state = GraphState(
            request_id="test-2",
            user_message="Test message",
            target_agents=[],
        )
        
        result = route_to_agents(state)
        
        assert result == "aggregate"

    def test_routes_to_single_agent(self):
        """Route correctly to a single specified agent."""
        for agent in VALID_AGENTS:
            state = GraphState(
                request_id=f"test-{agent}",
                user_message="Test message",
                target_agents=[agent],
            )
            
            result = route_to_agents(state)
            
            assert result == agent

    def test_skips_invalid_agents(self):
        """Skip invalid agents and route to first valid one."""
        state = GraphState(
            request_id="test-3",
            user_message="Test message",
            target_agents=["invalid_agent", "marketing"],
        )
        
        result = route_to_agents(state)
        
        assert result == "marketing"

    def test_routes_to_aggregate_when_all_invalid(self):
        """Route to aggregate when all agents are invalid."""
        state = GraphState(
            request_id="test-4",
            user_message="Test message",
            target_agents=["invalid1", "invalid2"],
        )
        
        result = route_to_agents(state)
        
        assert result == "aggregate"


class TestCreateAgentAssignments:
    """Tests for agent assignment creation."""

    def test_creates_assignments_for_all_agents(self):
        """Create assignments for all valid agents."""
        agents = ["partnerships", "finance", "marketing"]
        user_message = "Update sponsor status"
        
        assignments = create_agent_assignments(agents, user_message)
        
        assert len(assignments) == 3
        assert all(isinstance(a, AgentAssignment) for a in assignments)

    def test_assignment_contains_correct_agent_name(self):
        """Assignments contain correct agent names."""
        agents = ["partnerships"]
        user_message = "Test"
        
        assignments = create_agent_assignments(agents, user_message)
        
        assert assignments[0].agent_name == "partnerships"

    def test_assignment_contains_sub_prompt(self):
        """Assignments contain sub-prompts."""
        agents = ["events"]
        user_message = "Book room 301"
        
        assignments = create_agent_assignments(agents, user_message)
        
        assert assignments[0].sub_prompt == user_message

    def test_filters_invalid_agents(self):
        """Invalid agents are filtered out."""
        agents = ["partnerships", "invalid_agent", "finance"]
        user_message = "Test"
        
        assignments = create_agent_assignments(agents, user_message)
        
        assert len(assignments) == 2
        agent_names = [a.agent_name for a in assignments]
        assert "invalid_agent" not in agent_names


class TestRouterNode:
    """Tests for the router node function."""

    @pytest.mark.asyncio
    async def test_creates_router_output(self):
        """Router node creates RouterOutput."""
        state = GraphState(
            request_id="test-1",
            user_message="Test message",
            target_agents=["partnerships", "finance"],
        )
        
        result = await router_node(state)
        
        assert "router_output" in result
        assert isinstance(result["router_output"], RouterOutput)

    @pytest.mark.asyncio
    async def test_sets_parallel_flag_for_multiple_agents(self):
        """Parallel flag is set when multiple agents are assigned."""
        state = GraphState(
            request_id="test-2",
            user_message="Test message",
            target_agents=["partnerships", "finance"],
        )
        
        result = await router_node(state)
        
        assert result["router_output"].should_execute_parallel is True

    @pytest.mark.asyncio
    async def test_unsets_parallel_flag_for_single_agent(self):
        """Parallel flag is unset for single agent."""
        state = GraphState(
            request_id="test-3",
            user_message="Test message",
            target_agents=["partnerships"],
        )
        
        result = await router_node(state)
        
        assert result["router_output"].should_execute_parallel is False

    @pytest.mark.asyncio
    async def test_empty_assignments_for_no_agents(self):
        """Empty assignments when no agents specified."""
        state = GraphState(
            request_id="test-4",
            user_message="Test message",
            target_agents=[],
        )
        
        result = await router_node(state)
        
        assert result["router_output"].assignments == []


class TestHelperFunctions:
    """Tests for router helper functions."""

    def test_get_all_target_agents_filters_valid(self):
        """get_all_target_agents returns only valid agents."""
        state = GraphState(
            request_id="test-1",
            user_message="Test",
            target_agents=["partnerships", "invalid", "marketing"],
        )
        
        result = get_all_target_agents(state)
        
        assert result == ["partnerships", "marketing"]

    def test_get_parallel_agent_nodes_returns_agents(self):
        """get_parallel_agent_nodes returns agent list."""
        state = GraphState(
            request_id="test-2",
            user_message="Test",
            target_agents=["finance", "events"],
        )
        
        result = get_parallel_agent_nodes(state)
        
        assert "finance" in result
        assert "events" in result

    def test_get_parallel_agent_nodes_returns_aggregate_when_empty(self):
        """get_parallel_agent_nodes returns aggregate for empty agents."""
        state = GraphState(
            request_id="test-3",
            user_message="Test",
            target_agents=[],
        )
        
        result = get_parallel_agent_nodes(state)
        
        assert result == ["aggregate"]

    def test_should_run_agent_returns_true(self):
        """should_run_agent returns True when agent is in list."""
        state = GraphState(
            request_id="test-4",
            user_message="Test",
            target_agents=["partnerships", "finance"],
        )
        
        check_partnerships = should_run_agent("partnerships")
        
        assert check_partnerships(state) is True

    def test_should_run_agent_returns_false(self):
        """should_run_agent returns False when agent not in list."""
        state = GraphState(
            request_id="test-5",
            user_message="Test",
            target_agents=["partnerships"],
        )
        
        check_marketing = should_run_agent("marketing")
        
        assert check_marketing(state) is False


class TestValidAgents:
    """Tests for valid agents constant."""

    def test_all_expected_agents_present(self):
        """All expected agents are in VALID_AGENTS."""
        expected = ["partnerships", "marketing", "finance", "events", "developers"]
        for agent in expected:
            assert agent in VALID_AGENTS

    def test_valid_agents_count(self):
        """Correct number of valid agents."""
        assert len(VALID_AGENTS) == 5
