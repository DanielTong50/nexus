"""Classifier node for routing user requests to specialized agents.

Uses Gemini 3 Pro to analyze user messages and determine which agent(s)
should handle them. Returns structured classification with confidence scores.
"""

import json
import logging
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from config.prompts import CLASSIFIER_SYSTEM_PROMPT, CLASSIFIER_USER_PROMPT
from config.settings import settings
from src.models.state import GraphState

logger = logging.getLogger(__name__)

# Valid agent names
VALID_AGENTS = ["partnerships", "marketing", "finance", "events", "developers"]

# Request types for classification
RequestType = Literal["status_update", "question", "task", "info_request", "unknown"]


class ClassifierResponse(BaseModel):
    """Structured response from the classifier LLM."""

    request_type: RequestType = Field(
        default="unknown",
        description="Type of user request",
    )
    target_agents: list[str] = Field(
        default_factory=list,
        description="List of agent names to handle this request",
    )
    sub_prompts: list[str] = Field(
        default_factory=list,
        description="Sub-tasks derived from the main request",
    )
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confidence score for the classification",
    )
    reasoning: str = Field(
        default="",
        description="Brief explanation of the classification decision",
    )


def _get_classifier_llm() -> ChatGoogleGenerativeAI:
    """Get the LLM instance for classification."""
    return ChatGoogleGenerativeAI(
        model=settings.classifier_model,
        google_api_key=settings.google_api_key,
        temperature=0.1,  # Low temperature for consistent classification
        convert_system_message_to_human=True,
    )


def _parse_llm_response(content: str) -> list[str]:
    """Parse LLM response to extract agent names.

    Args:
        content: Raw LLM response string

    Returns:
        List of valid agent names
    """
    try:
        # Try to parse as JSON
        # Handle cases where response might have markdown code blocks
        content = content.strip()
        if content.startswith("```"):
            # Extract content between code blocks
            lines = content.split("\n")
            content = "\n".join(lines[1:-1]) if len(lines) > 2 else content

        # Try direct JSON parse
        data = json.loads(content)

        # Handle both list and dict responses
        if isinstance(data, list):
            agents = data
        elif isinstance(data, dict):
            # Look for common keys
            agents = data.get("target_agents", data.get("agents", []))
        else:
            agents = []

        # Filter to valid agents only
        return [a.lower().strip() for a in agents if a.lower().strip() in VALID_AGENTS]

    except json.JSONDecodeError:
        logger.warning(f"Failed to parse classifier response as JSON: {content}")
        # Fallback: try to find agent names in the text
        found_agents = []
        content_lower = content.lower()
        for agent in VALID_AGENTS:
            if agent in content_lower:
                found_agents.append(agent)
        return found_agents


async def classify_request(state: GraphState) -> dict:
    """Classify the user request and determine target agents.

    This node analyzes the user message using Gemini 3 Pro and decides
    which specialized agents should handle the request.

    Args:
        state: Current graph state containing user_message

    Returns:
        Dict with target_agents list to update graph state
    """
    user_message = state.user_message

    if not user_message or not user_message.strip():
        logger.warning("Empty user message received")
        return {"target_agents": []}

    try:
        llm = _get_classifier_llm()

        # Format the prompts
        system_msg = SystemMessage(content=CLASSIFIER_SYSTEM_PROMPT)
        user_msg = HumanMessage(
            content=CLASSIFIER_USER_PROMPT.format(user_request=user_message)
        )

        # Call the LLM
        response = await llm.ainvoke([system_msg, user_msg])
        content = response.content

        logger.info(f"Classifier raw response: {content}")

        # Parse the response
        target_agents = _parse_llm_response(content)

        if not target_agents:
            logger.warning(f"No agents identified for request: {user_message[:100]}")

        logger.info(f"Classified request to agents: {target_agents}")

        return {"target_agents": target_agents}

    except Exception as e:
        logger.error(f"Classification failed: {e}")
        # On error, return empty list - workflow will handle gracefully
        return {"target_agents": [], "errors": [{"type": "classification_error", "message": str(e)}]}


async def classify_with_details(user_message: str) -> ClassifierResponse:
    """Classify a request and return detailed response.

    This is a standalone function for testing and detailed classification.

    Args:
        user_message: The user's request text

    Returns:
        ClassifierResponse with full classification details
    """
    if not user_message or not user_message.strip():
        return ClassifierResponse(target_agents=[], reasoning="Empty request")

    try:
        llm = _get_classifier_llm()

        # Enhanced prompt for detailed response
        detailed_prompt = f"""Analyze this request and classify it.

Request: {user_message}

Respond with JSON in this exact format:
{{
    "request_type": "status_update" | "question" | "task" | "info_request" | "unknown",
    "target_agents": ["agent1", "agent2"],
    "sub_prompts": ["sub-task 1", "sub-task 2"],
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation"
}}

Available agents: partnerships, marketing, finance, events, developers"""

        system_msg = SystemMessage(content=CLASSIFIER_SYSTEM_PROMPT)
        user_msg = HumanMessage(content=detailed_prompt)

        response = await llm.ainvoke([system_msg, user_msg])
        content = response.content.strip()

        # Clean markdown if present
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1]) if len(lines) > 2 else content

        data = json.loads(content)

        # Validate agents
        valid_agents = [a for a in data.get("target_agents", []) if a.lower() in VALID_AGENTS]

        return ClassifierResponse(
            request_type=data.get("request_type", "unknown"),
            target_agents=valid_agents,
            sub_prompts=data.get("sub_prompts", []),
            confidence=data.get("confidence", 0.5),
            reasoning=data.get("reasoning", ""),
        )

    except Exception as e:
        logger.error(f"Detailed classification failed: {e}")
        return ClassifierResponse(
            target_agents=[],
            reasoning=f"Classification error: {str(e)}",
        )
