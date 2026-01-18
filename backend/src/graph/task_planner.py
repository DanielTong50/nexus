"""Task Planner for intelligent workflow decomposition.

Uses an LLM to analyze user requests and decompose them into structured
task plans with dependencies, entity extraction, and execution strategies.

The LLM receives organization context with all available channels/data sources
and outputs exact names directly - no post-processing resolution needed.
"""

import json
import logging
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from config.prompts import TASK_PLANNER_SYSTEM_PROMPT
from config.settings import settings
from src.models.state import GraphState
from src.models.task_plan import (
    TaskPlan,
    Task,
    ExtractedEntity,
    create_task_plan,
    RequestType,
    ExecutionStrategy,
)
from src.services.organization import org_service, DEFAULT_ORG_ID

logger = logging.getLogger(__name__)


class TaskPlannerResponse(BaseModel):
    """Structured response from the task planner LLM."""
    
    request_type: RequestType = Field(
        default="workflow",
        description="Type of user request",
    )
    extracted_entities: list[dict] = Field(
        default_factory=list,
        description="Entities extracted from the message",
    )
    tasks: list[dict] = Field(
        default_factory=list,
        description="List of tasks to execute",
    )
    execution_strategy: ExecutionStrategy = Field(
        default="sequential",
        description="How tasks should be executed",
    )
    reasoning: str = Field(
        default="",
        description="Explanation of the decomposition",
    )


def _get_planner_llm() -> ChatGoogleGenerativeAI:
    """Get the LLM instance for task planning."""
    return ChatGoogleGenerativeAI(
        model=settings.classifier_model,  # Use same model as classifier
        google_api_key=settings.google_api_key,
        temperature=0.1,  # Low temperature for consistent structured output
        convert_system_message_to_human=True,
    )


def _parse_llm_response(content: str) -> dict:
    """Parse LLM response to extract task plan.
    
    Args:
        content: Raw LLM response string
        
    Returns:
        Parsed task plan dictionary
    """
    # Clean markdown code blocks if present
    content = content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        # Remove first line (```json) and last line (```)
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines)
    
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse task planner response: {e}")
        logger.error(f"Raw content: {content[:500]}")
        raise ValueError(f"Invalid JSON response from task planner: {e}")


def _build_system_prompt(org_context: str) -> str:
    """Build the system prompt with organization context.
    
    Args:
        org_context: Formatted organization context string
        
    Returns:
        Complete system prompt
    """
    # Get example values from context for the template
    # Default values if parsing fails
    example_channel = "#partnerships"
    example_sheet = "Boothing Companies"
    
    # Try to extract actual values from context
    if "#" in org_context:
        # Find first channel in context
        for line in org_context.split("\n"):
            if line.strip().startswith("- #"):
                example_channel = line.strip().split()[1].rstrip(")")
                break
    
    if "Boothing" in org_context or "Companies" in org_context:
        example_sheet = "Boothing Companies"
    
    return TASK_PLANNER_SYSTEM_PROMPT.format(
        org_context=org_context,
        example_channel=example_channel,
        example_sheet=example_sheet,
    )


async def plan_tasks(state: GraphState) -> dict:
    """Plan tasks from user message with organization context.
    
    This is the main entry point for the task planner. It:
    1. Loads organization context
    2. Calls the LLM with the task planner prompt
    3. Parses the response into a TaskPlan
    4. Updates the graph state
    
    Args:
        state: Current graph state containing user_message and org_id
        
    Returns:
        Dict with task_plan and target_agents to update graph state
    """
    user_message = state.user_message
    org_id = state.org_id or DEFAULT_ORG_ID
    
    if not user_message or not user_message.strip():
        logger.warning("Empty user message received")
        return {
            "target_agents": [],
            "task_plan": None,
        }
    
    try:
        # Get organization context for the prompt
        org_context = await org_service.get_prompt_context_string(org_id)
        
        # Build the system prompt with org context
        system_prompt = _build_system_prompt(org_context)
        
        # Create messages
        llm = _get_planner_llm()
        system_msg = SystemMessage(content=system_prompt)
        user_msg = HumanMessage(content=f"Plan tasks for this request:\n\n{user_message}")
        
        # Call the LLM
        response = await llm.ainvoke([system_msg, user_msg])
        content = response.content
        
        logger.info(f"Task planner raw response: {content[:500]}...")
        
        # Parse the response
        plan_data = _parse_llm_response(content)
        
        # Convert to TaskPlan model
        task_plan = _create_task_plan_from_response(plan_data, state.request_id)
        
        # Extract target agents for backward compatibility
        target_agents = list(set(task.agent for task in task_plan.tasks))
        
        logger.info(f"Created task plan with {len(task_plan.tasks)} tasks for agents: {target_agents}")
        
        return {
            "target_agents": target_agents,
            "task_plan": task_plan,
        }
        
    except Exception as e:
        logger.error(f"Task planning failed: {e}")
        return {
            "target_agents": [],
            "task_plan": None,
            "errors": [{"type": "task_planning_error", "message": str(e)}],
        }


def _create_task_plan_from_response(data: dict, request_id: str) -> TaskPlan:
    """Create a TaskPlan from the LLM response.
    
    Args:
        data: Parsed LLM response dictionary
        request_id: Request identifier
        
    Returns:
        TaskPlan instance
    """
    # Parse extracted entities
    entities = []
    for entity_data in data.get("extracted_entities", []):
        entities.append(ExtractedEntity(
            entity_type=entity_data.get("entity_type", "unknown"),
            value=entity_data.get("value", ""),
            confidence=entity_data.get("confidence", 0.5),
        ))
    
    # Parse tasks
    tasks = []
    for task_data in data.get("tasks", []):
        tasks.append(Task(
            id=task_data.get("id", f"task_{len(tasks)+1}"),
            agent=task_data.get("agent", "events"),
            action=task_data.get("action", "unknown"),
            parameters=task_data.get("parameters", {}),
            description=task_data.get("description", ""),
            depends_on=task_data.get("depends_on", []),
            requires_approval=task_data.get("requires_approval", False),
        ))
    
    # Determine target agents
    target_agents = list(set(task.agent for task in tasks))
    
    return TaskPlan(
        plan_id=f"plan_{request_id}",
        request_id=request_id,
        request_type=data.get("request_type", "workflow"),
        tasks=tasks,
        extracted_entities=entities,
        execution_strategy=data.get("execution_strategy", "sequential"),
        target_agents=target_agents,
    )


async def plan_tasks_standalone(
    user_message: str,
    org_id: str = DEFAULT_ORG_ID,
    request_id: str = "standalone",
) -> TaskPlan:
    """Plan tasks for a message without a full graph state.
    
    Useful for testing and direct API calls.
    
    Args:
        user_message: The user's request text
        org_id: Organization identifier
        request_id: Request identifier
        
    Returns:
        TaskPlan with decomposed tasks
    """
    if not user_message or not user_message.strip():
        return TaskPlan(
            plan_id=f"plan_{request_id}",
            request_id=request_id,
            request_type="workflow",
            tasks=[],
            target_agents=[],
        )
    
    try:
        # Get organization context
        org_context = await org_service.get_prompt_context_string(org_id)
        
        # Build prompt and call LLM
        system_prompt = _build_system_prompt(org_context)
        llm = _get_planner_llm()
        
        system_msg = SystemMessage(content=system_prompt)
        user_msg = HumanMessage(content=f"Plan tasks for this request:\n\n{user_message}")
        
        response = await llm.ainvoke([system_msg, user_msg])
        plan_data = _parse_llm_response(response.content)
        
        return _create_task_plan_from_response(plan_data, request_id)
        
    except Exception as e:
        logger.error(f"Standalone task planning failed: {e}")
        raise


# Backward compatibility: simple classification
async def classify_to_agents(user_message: str, org_id: str = DEFAULT_ORG_ID) -> list[str]:
    """Simple classification returning just agent names.
    
    Backward-compatible function that uses the task planner but
    only returns the list of target agents.
    
    Args:
        user_message: The user's request text
        org_id: Organization identifier
        
    Returns:
        List of agent names that should handle the request
    """
    try:
        plan = await plan_tasks_standalone(user_message, org_id)
        return plan.target_agents
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        return []
