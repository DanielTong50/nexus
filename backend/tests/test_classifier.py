"""Tests for the classifier node.

Tests verify that the classifier correctly routes user requests
to the appropriate agent(s).
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.graph.classifier import (
    classify_request,
    classify_with_details,
    _parse_llm_response,
    ClassifierResponse,
    VALID_AGENTS,
)
from src.models.state import GraphState


class TestParseResponse:
    """Tests for the LLM response parser."""

    def test_parse_json_array(self):
        """Parse simple JSON array response."""
        response = '["partnerships", "finance"]'
        result = _parse_llm_response(response)
        assert result == ["partnerships", "finance"]

    def test_parse_json_with_markdown(self):
        """Parse JSON wrapped in markdown code blocks."""
        response = '```json\n["marketing", "events"]\n```'
        result = _parse_llm_response(response)
        assert result == ["marketing", "events"]

    def test_parse_json_object_with_target_agents(self):
        """Parse JSON object with target_agents key."""
        response = '{"target_agents": ["developers", "partnerships"]}'
        result = _parse_llm_response(response)
        assert result == ["developers", "partnerships"]

    def test_filter_invalid_agents(self):
        """Filter out invalid agent names."""
        response = '["partnerships", "invalid_agent", "finance", "fake"]'
        result = _parse_llm_response(response)
        assert result == ["partnerships", "finance"]

    def test_fallback_text_extraction(self):
        """Extract agent names from non-JSON text."""
        response = "Based on the request, I recommend the partnerships and marketing agents."
        result = _parse_llm_response(response)
        assert "partnerships" in result
        assert "marketing" in result

    def test_empty_response(self):
        """Handle empty response."""
        result = _parse_llm_response("")
        assert result == []

    def test_case_insensitive(self):
        """Handle mixed case agent names."""
        response = '["PARTNERSHIPS", "Marketing", "FINANCE"]'
        result = _parse_llm_response(response)
        assert "partnerships" in result
        assert "marketing" in result
        assert "finance" in result


class TestClassifyRequest:
    """Tests for the main classify_request function."""

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM for testing."""
        with patch("src.graph.classifier._get_classifier_llm") as mock:
            llm_instance = AsyncMock()
            mock.return_value = llm_instance
            yield llm_instance

    @pytest.mark.asyncio
    async def test_partnerships_classification(self, mock_llm):
        """Test classification of partnerships-related request."""
        mock_llm.ainvoke.return_value = MagicMock(content='["partnerships"]')
        
        state = GraphState(
            request_id="test-1",
            user_message="Update the sponsor status for Google to confirmed",
        )
        
        result = await classify_request(state)
        
        assert "partnerships" in result["target_agents"]

    @pytest.mark.asyncio
    async def test_marketing_classification(self, mock_llm):
        """Test classification of marketing-related request."""
        mock_llm.ainvoke.return_value = MagicMock(content='["marketing"]')
        
        state = GraphState(
            request_id="test-2",
            user_message="Schedule an Instagram post for Blueprint launch",
        )
        
        result = await classify_request(state)
        
        assert "marketing" in result["target_agents"]

    @pytest.mark.asyncio
    async def test_finance_classification(self, mock_llm):
        """Test classification of finance-related request."""
        mock_llm.ainvoke.return_value = MagicMock(content='["finance"]')
        
        state = GraphState(
            request_id="test-3",
            user_message="What's the remaining budget for Blueprint?",
        )
        
        result = await classify_request(state)
        
        assert "finance" in result["target_agents"]

    @pytest.mark.asyncio
    async def test_events_classification(self, mock_llm):
        """Test classification of events-related request."""
        mock_llm.ainvoke.return_value = MagicMock(content='["events"]')
        
        state = GraphState(
            request_id="test-4",
            user_message="Book room 301 in the engineering building for Saturday",
        )
        
        result = await classify_request(state)
        
        assert "events" in result["target_agents"]

    @pytest.mark.asyncio
    async def test_developers_classification(self, mock_llm):
        """Test classification of developers-related request."""
        mock_llm.ainvoke.return_value = MagicMock(content='["developers"]')
        
        state = GraphState(
            request_id="test-5",
            user_message="Create a GitHub issue for the registration page bug",
        )
        
        result = await classify_request(state)
        
        assert "developers" in result["target_agents"]

    @pytest.mark.asyncio
    async def test_multi_agent_classification(self, mock_llm):
        """Test classification routing to multiple agents."""
        mock_llm.ainvoke.return_value = MagicMock(
            content='["partnerships", "finance", "marketing", "events"]'
        )
        
        state = GraphState(
            request_id="test-6",
            user_message="Just finished a meeting with Google who agreed to pay $1,000 for boothing at Blueprint",
        )
        
        result = await classify_request(state)
        
        # This request should trigger multiple agents
        assert len(result["target_agents"]) >= 2
        assert "partnerships" in result["target_agents"]
        assert "finance" in result["target_agents"]

    @pytest.mark.asyncio
    async def test_empty_message(self, mock_llm):
        """Test handling of empty user message."""
        state = GraphState(
            request_id="test-7",
            user_message="",
        )
        
        result = await classify_request(state)
        
        assert result["target_agents"] == []
        # LLM should not be called for empty message
        mock_llm.ainvoke.assert_not_called()

    @pytest.mark.asyncio
    async def test_llm_error_handling(self, mock_llm):
        """Test handling of LLM errors."""
        mock_llm.ainvoke.side_effect = Exception("API error")
        
        state = GraphState(
            request_id="test-8",
            user_message="Some valid request",
        )
        
        result = await classify_request(state)
        
        # Should return empty list on error
        assert result["target_agents"] == []
        # Should include error info
        assert "errors" in result


class TestClassifyWithDetails:
    """Tests for the detailed classification function."""

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM for testing."""
        with patch("src.graph.classifier._get_classifier_llm") as mock:
            llm_instance = AsyncMock()
            mock.return_value = llm_instance
            yield llm_instance

    @pytest.mark.asyncio
    async def test_detailed_response(self, mock_llm):
        """Test that detailed classification returns all fields."""
        mock_llm.ainvoke.return_value = MagicMock(
            content='''{
                "request_type": "status_update",
                "target_agents": ["partnerships", "finance"],
                "sub_prompts": ["Update sponsor status", "Generate invoice"],
                "confidence": 0.95,
                "reasoning": "Request is about sponsor confirmation"
            }'''
        )
        
        result = await classify_with_details("Sponsor confirmed payment")
        
        assert isinstance(result, ClassifierResponse)
        assert result.request_type == "status_update"
        assert "partnerships" in result.target_agents
        assert result.confidence == 0.95

    @pytest.mark.asyncio
    async def test_empty_request_returns_empty_response(self, mock_llm):
        """Test that empty request returns empty ClassifierResponse."""
        result = await classify_with_details("")
        
        assert result.target_agents == []
        assert "Empty request" in result.reasoning


class TestValidAgents:
    """Tests for agent validation."""

    def test_all_valid_agents_present(self):
        """Verify all expected agents are in VALID_AGENTS."""
        expected = ["partnerships", "marketing", "finance", "events", "developers"]
        for agent in expected:
            assert agent in VALID_AGENTS
