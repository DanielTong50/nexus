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

    def test_parse_json_with_target_agents(self):
        """Parse JSON object with target_agents key."""
        response = '{"request_type": "sponsor", "target_agents": ["developers", "partnerships"], "confidence": 0.9, "reasoning": "test"}'
        result = _parse_llm_response(response)
        assert isinstance(result, ClassifierResponse)
        assert result.target_agents == ["developers", "partnerships"]

    def test_parse_json_with_markdown(self):
        """Parse JSON wrapped in markdown code blocks."""
        response = '```json\n{"request_type": "test", "target_agents": ["marketing", "events"]}\n```'
        result = _parse_llm_response(response)
        assert result.target_agents == ["marketing", "events"]

    def test_filter_invalid_agents(self):
        """Filter out invalid agent names."""
        response = '{"target_agents": ["partnerships", "invalid_agent", "finance", "fake"]}'
        result = _parse_llm_response(response)
        assert result.target_agents == ["partnerships", "finance"]

    def test_fallback_text_extraction(self):
        """Extract agent names from non-JSON text."""
        response = "Based on the request, I recommend the partnerships and marketing agents."
        result = _parse_llm_response(response)
        assert "partnerships" in result.target_agents
        assert "marketing" in result.target_agents

    def test_empty_response(self):
        """Empty response returns empty targets."""
        response = "{}"
        result = _parse_llm_response(response)
        assert result.target_agents == []

    def test_case_insensitive(self):
        """Agent names are case-insensitive."""
        response = '{"target_agents": ["Partnerships", "MARKETING"]}'
        result = _parse_llm_response(response)
        assert "partnerships" in result.target_agents
        assert "marketing" in result.target_agents


class TestClassifyRequest:
    """Tests for the classify_request function."""

    @pytest.fixture
    def mock_llm(self):
        """Mock the LLM for testing."""
        patcher = patch("src.graph.classifier._get_classifier_llm")
        mock = patcher.start()
        llm_instance = MagicMock()
        mock.return_value = llm_instance
        yield llm_instance
        patcher.stop()

    @pytest.fixture
    def base_state(self):
        """Create a base state for tests."""
        return GraphState(
            request_id="test-123",
            user_message="",
        )

    @pytest.mark.asyncio
    async def test_partnerships_classification(self, base_state):
        """Classify partnerships-related request."""
        base_state.user_message = "Update the sponsor sheet for Google"

        mock_response = MagicMock()
        mock_response.content = '{"request_type": "sponsor", "target_agents": ["partnerships"], "confidence": 0.9, "reasoning": "sponsor related"}'
        
        with patch("src.graph.classifier._get_classifier_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            mock_get_llm.return_value = mock_llm

            result = await classify_request(base_state)

        assert "partnerships" in result["target_agents"]

    @pytest.mark.asyncio
    async def test_marketing_classification(self, mock_llm, base_state):
        """Classify marketing-related request."""
        base_state.user_message = "Schedule an Instagram post for Blueprint"

        mock_response = MagicMock()
        mock_response.content = '{"request_type": "social", "target_agents": ["marketing"], "confidence": 0.9, "reasoning": "social media"}'
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await classify_request(base_state)

        assert "marketing" in result["target_agents"]

    @pytest.mark.asyncio
    async def test_finance_classification(self, mock_llm, base_state):
        """Classify finance-related request."""
        base_state.user_message = "Generate an invoice for Microsoft sponsorship"

        mock_response = MagicMock()
        mock_response.content = '{"request_type": "invoice", "target_agents": ["finance"], "confidence": 0.9, "reasoning": "financial"}'
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await classify_request(base_state)

        assert "finance" in result["target_agents"]

    @pytest.mark.asyncio
    async def test_events_classification(self, mock_llm, base_state):
        """Classify events-related request."""
        base_state.user_message = "Update the venue logistics sheet"

        mock_response = MagicMock()
        mock_response.content = '{"request_type": "logistics", "target_agents": ["events"], "confidence": 0.9, "reasoning": "event related"}'
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await classify_request(base_state)

        assert "events" in result["target_agents"]

    @pytest.mark.asyncio
    async def test_developers_classification(self, mock_llm, base_state):
        """Classify developers-related request."""
        base_state.user_message = "Create a GitHub issue for the login bug"

        mock_response = MagicMock()
        mock_response.content = '{"request_type": "github", "target_agents": ["developers"], "confidence": 0.9, "reasoning": "technical"}'
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await classify_request(base_state)

        assert "developers" in result["target_agents"]

    @pytest.mark.asyncio
    async def test_multi_agent_classification(self, mock_llm, base_state):
        """Classify request requiring multiple agents."""
        base_state.user_message = "Google agreed to sponsor for $5000, update the sheet and draft the MOU"

        mock_response = MagicMock()
        mock_response.content = '{"request_type": "sponsor_mou", "target_agents": ["partnerships", "finance"], "confidence": 0.9, "reasoning": "sponsor and financial"}'
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await classify_request(base_state)

        assert "partnerships" in result["target_agents"]
        assert "finance" in result["target_agents"]


class TestClassifyWithDetails:
    """Tests for the classify_with_details function."""

    @pytest.fixture
    def mock_llm(self):
        """Mock the LLM for testing."""
        patcher = patch("src.graph.classifier._get_classifier_llm")
        mock = patcher.start()
        llm_instance = MagicMock()
        mock.return_value = llm_instance
        yield llm_instance
        patcher.stop()

    @pytest.mark.asyncio
    async def test_detailed_response(self, mock_llm):
        """Get detailed classification response."""
        mock_response = MagicMock()
        mock_response.content = '{"request_type": "sponsor", "target_agents": ["partnerships"], "confidence": 0.95, "reasoning": "This is about sponsors"}'
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await classify_with_details("Update sponsor status")

        assert isinstance(result, ClassifierResponse)
        assert result.confidence == 0.95
        assert "partnerships" in result.target_agents

    @pytest.mark.asyncio
    async def test_empty_request_returns_empty_response(self, mock_llm):
        """Empty request returns empty classification."""
        mock_response = MagicMock()
        mock_response.content = '{"request_type": "empty", "target_agents": [], "confidence": 0.0, "reasoning": "Empty message"}'
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        result = await classify_with_details("")

        assert result.target_agents == []


class TestValidAgents:
    """Tests for valid agent list."""

    def test_all_expected_agents_present(self):
        """All expected agents are in VALID_AGENTS."""
        expected = {"partnerships", "marketing", "finance", "events", "developers"}
        assert VALID_AGENTS == expected
