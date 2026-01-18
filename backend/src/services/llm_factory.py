"""
LLM Factory for Nexus.

Provides LLM instances based on agent type and configuration.
Routes specific agents to Vultr (cost-effective) and others to Gemini.
"""

import logging
from typing import Literal, Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from config.settings import settings

logger = logging.getLogger(__name__)

# Agents that use Vultr (Llama 3.3 70B) - less critical, cost-effective
VULTR_AGENTS = ["events", "developers"]

# Agents that use Gemini - critical operations
GEMINI_AGENTS = ["partnerships", "marketing", "finance", "classifier"]


def get_llm_for_agent(
    agent_name: str,
    temperature: float = 0.3,
    force_provider: Optional[Literal["gemini", "vultr"]] = None,
):
    """
    Get the appropriate LLM for an agent.

    Args:
        agent_name: Name of the agent (events, developers, partnerships, etc.)
        temperature: LLM temperature setting
        force_provider: Override automatic provider selection

    Returns:
        LLM instance (ChatGoogleGenerativeAI or ChatOpenAI for Vultr)
    """
    # Determine provider
    if force_provider:
        provider = force_provider
    elif agent_name.lower() in VULTR_AGENTS and settings.vultr_api_key:
        provider = "vultr"
    else:
        provider = "gemini"

    if provider == "vultr":
        logger.info(f"Using Vultr (Llama 3.3 70B) for agent: {agent_name}")
        return ChatOpenAI(
            base_url=settings.vultr_inference_url,
            api_key=settings.vultr_api_key,
            model=settings.vultr_agent_model,
            temperature=temperature,
        )
    else:
        logger.info(f"Using Gemini for agent: {agent_name}")
        return ChatGoogleGenerativeAI(
            model=settings.agent_model,
            google_api_key=settings.google_api_key,
            temperature=temperature,
        )


def get_classifier_llm(temperature: float = 0.1):
    """
    Get LLM for the classifier. Always uses Gemini for reliability.
    """
    return ChatGoogleGenerativeAI(
        model=settings.classifier_model,
        google_api_key=settings.google_api_key,
        temperature=temperature,
    )
