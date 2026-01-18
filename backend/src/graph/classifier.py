"""Request classifier using Gemini 1.5 Pro.

The classifier always uses Gemini (not Vultr) as it requires
high accuracy for routing decisions.
"""

import logging
import re
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from config.settings import settings
from src.models.state import GraphState

logger = logging.getLogger(__name__)

# Valid agents for routing
VALID_AGENTS = {"partnerships", "marketing", "finance", "events", "developers"}


class ClassifierResponse(BaseModel):
    """Structured response from the classifier."""

    request_type: str = Field(description="Type of request")
    target_agents: list[str] = Field(description="List of agents to handle this request")
    sub_prompts: dict[str, str] = Field(
        default_factory=dict, description="Agent-specific prompts"
    )
    confidence: float = Field(default=0.8, description="Confidence score")
    reasoning: str = Field(default="", description="Explanation for routing")


CLASSIFIER_PROMPT = """You are a request classifier for an event production platform called Nexus.

Your job is to analyze user messages and determine which agent(s) should handle the request.

Available agents:
- partnerships: Sponsors, judges, mentors, partner outreach, MOUs
- marketing: Social media, content creation, promotions, branding
- finance: Budgets, expenses, invoices, financial tracking
- events: Event logistics, scheduling, venues, coordination
- developers: Technical tasks, GitHub, development workflows

Rules:
1. A request can be routed to MULTIPLE agents if it spans domains
2. Return agent names in lowercase, exactly matching the list above
3. Provide reasoning for your classification
4. Be conservative - only route to agents that are clearly needed

Respond in JSON format:
{
  "request_type": "brief description",
  "target_agents": ["agent1", "agent2"],
  "confidence": 0.9,
  "reasoning": "why these agents"
}

User message: {message}
"""


def _get_classifier_llm() -> ChatGoogleGenerativeAI:
    """Get the classifier LLM (always Gemini 1.5 Pro)."""
    return ChatGoogleGenerativeAI(
        model=settings.classifier_model,
        google_api_key=settings.gemini_api_key.get_secret_value(),
        temperature=0.1,
    )


def _parse_llm_response(content: str) -> ClassifierResponse:
    """Parse LLM response to ClassifierResponse.

    Args:
        content: LLM response content

    Returns:
        ClassifierResponse with parsed data
    """
    import json

    # Try to extract JSON from response
    content = content.strip()

    # Remove markdown code blocks if present
    if content.startswith("```"):
        content = re.sub(r"```(?:json)?\n?", "", content)
        content = content.strip()

    try:
        data = json.loads(content)
        # Filter to valid agents only
        target_agents = [a.lower() for a in data.get("target_agents", []) if a.lower() in VALID_AGENTS]

        return ClassifierResponse(
            request_type=data.get("request_type", "general"),
            target_agents=target_agents,
            confidence=data.get("confidence", 0.8),
            reasoning=data.get("reasoning", ""),
        )
    except json.JSONDecodeError:
        # Fallback: try to extract agent names from text
        logger.warning("Failed to parse JSON, extracting agents from text")
        found_agents = [agent for agent in VALID_AGENTS if agent in content.lower()]
        return ClassifierResponse(
            request_type="general",
            target_agents=found_agents,
            reasoning="Extracted from text response",
        )


async def classify_request(state: GraphState) -> dict:
    """Classify a user request and determine target agents.

    Args:
        state: Current graph state with user_message

    Returns:
        Dict with target_agents list
    """
    user_message = state.user_message

    if not user_message:
        logger.warning("Empty user message, no agents needed")
        return {"target_agents": []}

    try:
        llm = _get_classifier_llm()

        prompt = CLASSIFIER_PROMPT.format(message=user_message)
        messages = [HumanMessage(content=prompt)]

        response = await llm.ainvoke(messages)
        result = _parse_llm_response(response.content)

        logger.info(
            f"Classified request: {result.request_type} -> {result.target_agents} "
            f"(confidence: {result.confidence})"
        )

        return {
            "target_agents": result.target_agents,
            "next_step": "route" if result.target_agents else "aggregate",
        }

    except Exception as e:
        logger.error(f"Classification error: {e}")
        return {"target_agents": [], "errors": [str(e)]}


async def classify_with_details(message: str) -> ClassifierResponse:
    """Classify a message and return full details.

    Args:
        message: User message to classify

    Returns:
        Full ClassifierResponse with all fields
    """
    state = GraphState(user_message=message, request_id="classify-only")
    llm = _get_classifier_llm()

    prompt = CLASSIFIER_PROMPT.format(message=message)
    response = await llm.ainvoke([HumanMessage(content=prompt)])

    return _parse_llm_response(response.content)
