"""Server-Sent Events streaming utilities for real-time agent updates.

This module provides SSE streaming for the chat endpoint, allowing
the frontend to receive real-time updates as agents execute.

Supports two execution modes:
1. Legacy mode: Simple classification → parallel agent execution
2. Task mode: Task planning → dependency-aware orchestrated execution
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import AsyncGenerator, Optional

from sse_starlette.sse import EventSourceResponse

from src.graph.workflow import run_agents_parallel, AGENT_RUNNERS
from src.graph.classifier import classify_request
from src.graph.task_planner import plan_tasks
from src.graph.task_orchestrator import (
    TaskOrchestrator,
    TaskExecutor,
    TaskEvent,
    orchestrate_with_events,
)
from src.models.requests import ChatRequest, StreamEvent, PendingApproval
from src.models.approval import ApprovalDocument
from config.tool_requirements import (
    ACTION_TO_TOOL,
    get_missing_fields,
    get_clarification_questions,
)
from src.models.state import GraphState, AgentResult
from src.services.database import db_service
from src.repositories.approval_repository import ApprovalRepository
from src.repositories.chat_history_repository import ChatHistoryRepository

logger = logging.getLogger(__name__)


def _get_approval_repo() -> ApprovalRepository:
    """Get the approval repository instance."""
    return ApprovalRepository(db_service.db)


def _get_history_repo() -> ChatHistoryRepository:
    """Get the chat history repository instance."""
    return ChatHistoryRepository(db_service.db)

# Actions that require approval
ACTIONS_REQUIRING_APPROVAL = [
    "draft_mou",
    "generate_invoice",
    "schedule_instagram_post",
    "schedule_linkedin_post",
    "announce_to_slack",
]


def create_stream_event(
    event_type: str,
    data: dict,
    agent_name: Optional[str] = None,
) -> str:
    """Create a formatted SSE event string.

    Args:
        event_type: Type of event (classification, agent_start, etc.)
        data: Event data payload
        agent_name: Optional agent name for agent-specific events

    Returns:
        JSON string for SSE
    """
    event = StreamEvent(
        event_type=event_type,
        data=data,
        agent_name=agent_name,
        timestamp=datetime.utcnow(),
    )
    return json.dumps(event.model_dump(), default=str)


async def stream_classification(state: GraphState) -> tuple[dict, list[str]]:
    """Run classification and return result with target agents.

    Args:
        state: Initial graph state

    Returns:
        Tuple of (classification_result, target_agents)
    """
    result = await classify_request(state)
    target_agents = result.get("target_agents", [])
    return result, target_agents


async def stream_agent_execution(
    state: GraphState,
    agent_name: str,
) -> AsyncGenerator[str, None]:
    """Stream events for a single agent's execution.

    Args:
        state: Current graph state
        agent_name: Name of agent to execute

    Yields:
        SSE event strings
    """
    # Agent start event
    yield create_stream_event(
        "agent_start",
        {"message": f"{agent_name.title()} agent starting..."},
        agent_name=agent_name,
    )

    try:
        if agent_name in AGENT_RUNNERS:
            runner = AGENT_RUNNERS[agent_name]
            result = await runner(state)

            agent_results = result.get("agent_results", [])
            for agent_result in agent_results:
                # Check for tool calls
                if hasattr(agent_result, "tool_calls") and agent_result.tool_calls:
                    for tool_call in agent_result.tool_calls:
                        yield create_stream_event(
                            "agent_tool_call",
                            {
                                "tool": tool_call.get("name", "unknown"),
                                "status": "executing",
                            },
                            agent_name=agent_name,
                        )

                # Agent complete
                yield create_stream_event(
                    "agent_complete",
                    {
                        "status": agent_result.status,
                        "message": agent_result.message,
                        "data": agent_result.data,
                    },
                    agent_name=agent_name,
                )
        else:
            yield create_stream_event(
                "agent_error",
                {"error": f"Agent {agent_name} not found"},
                agent_name=agent_name,
            )

    except Exception as e:
        logger.error(f"Agent {agent_name} error: {e}")
        yield create_stream_event(
            "agent_error",
            {"error": str(e)},
            agent_name=agent_name,
        )


async def generate_events(request: ChatRequest) -> AsyncGenerator[str, None]:
    """Generate SSE events for a chat request.

    This is the main streaming function that:
    1. Classifies the request
    2. Routes to agents
    3. Streams agent execution updates
    4. Handles approvals if needed
    5. Returns final results

    Args:
        request: The chat request to process

    Yields:
        SSE event strings in real-time
    """
    request_id = request.request_id or str(uuid.uuid4())

    logger.info(f"Starting stream for request {request_id}: {request.message[:50]}...")

    # Create initial state
    state = GraphState(
        request_id=request_id,
        user_message=request.message,
        context=request.context,
    )

    try:
        # Step 1: Classification
        yield create_stream_event(
            "classification",
            {"message": "Analyzing request...", "request_id": request_id},
        )

        classification_result, target_agents = await stream_classification(state)

        yield create_stream_event(
            "routing",
            {
                "agents": target_agents,
                "message": f"Routing to {len(target_agents)} agent(s): {', '.join(target_agents)}" if target_agents else "No agents needed",
            },
        )

        if not target_agents:
            yield create_stream_event(
                "complete",
                {
                    "message": "No agents were needed for this request",
                    "results": [],
                    "request_id": request_id,
                },
            )
            return

        # Step 2: Execute agents in parallel, streaming updates
        # Update state with target agents
        state.target_agents = target_agents

        # Stream individual agent updates
        all_results: list[dict] = []
        pending_approval_ids: list[str] = []

        # Execute agents and stream their updates
        for agent_name in target_agents:
            async for event in stream_agent_execution(state, agent_name):
                yield event

                # Parse the event to check for results
                try:
                    event_data = json.loads(event)
                    if event_data.get("event_type") == "agent_complete":
                        all_results.append({
                            "agent_name": agent_name,
                            **event_data.get("data", {}),
                        })
                except json.JSONDecodeError:
                    pass

        # Step 3: Check for actions requiring approval
        approval_repo = _get_approval_repo()
        for result in all_results:
            if result.get("data") and result["data"].get("action_type") in ACTIONS_REQUIRING_APPROVAL:
                approval_id = str(uuid.uuid4())
                approval_doc = ApprovalDocument.create_with_expiry(
                    approval_id=approval_id,
                    request_id=request_id,
                    agent_name=result.get("agent_name", "unknown"),
                    action_type=result["data"]["action_type"],
                    action_description=result["data"].get("description", "Action requires approval"),
                    action_data=result["data"],
                    expiry_hours=24,
                )
                # Save to database
                await approval_repo.create(approval_doc)
                pending_approval_ids.append(approval_id)

                yield create_stream_event(
                    "approval_required",
                    {
                        "approval_id": approval_id,
                        "agent_name": approval_doc.agent_name,
                        "action_type": approval_doc.action_type,
                        "description": approval_doc.action_description,
                    },
                )

        # Step 4: Complete
        yield create_stream_event(
            "complete",
            {
                "message": "All agents completed",
                "request_id": request_id,
                "agents_invoked": target_agents,
                "results": all_results,
                "pending_approvals": pending_approval_ids,
            },
        )

    except Exception as e:
        logger.error(f"Stream error for request {request_id}: {e}")
        yield create_stream_event(
            "error",
            {
                "error": str(e),
                "request_id": request_id,
            },
        )


async def generate_events_parallel(request: ChatRequest) -> AsyncGenerator[str, None]:
    """Generate SSE events with true parallel agent execution.

    This version uses asyncio.gather for parallel execution while
    still streaming updates.

    Args:
        request: The chat request to process

    Yields:
        SSE event strings
    """
    request_id = request.request_id or str(uuid.uuid4())
    history_repo = _get_history_repo()

    state = GraphState(
        request_id=request_id,
        user_message=request.message,
        context=request.context,
    )

    try:
        # Log request start to database
        await history_repo.start_request(
            request_id=request_id,
            user_message=request.message,
            event_name=request.event_name,
            context=request.context,
        )

        # Check if this is a follow-up to a clarification request
        clarification_context = request.clarification_context
        if clarification_context and isinstance(clarification_context, dict):
            # Route directly to the agent that asked for clarification
            agent_name = clarification_context.get("agent_name", "")
            ctx = clarification_context.get("context", {})
            original_prompt = ctx.get("original_prompt", "")
            stored_entities = ctx.get("extracted_entities", {})
            tool_name = ctx.get("tool_name", "")
            
            if agent_name:
                target_agents = [agent_name]
                
                # Extract entities from the follow-up message
                classification_result = await classify_request(GraphState(
                    request_id=request_id,
                    user_message=request.message,
                ))
                new_entities = classification_result.get("extracted_entities", {})
                
                # Merge: new entities override stored ones
                merged_entities = {**stored_entities, **new_entities}
                
                # Re-check if all required fields are now present
                if tool_name:
                    missing_fields = get_missing_fields(tool_name, merged_entities)
                    
                    if missing_fields:
                        # Still missing fields - ask again
                        questions = get_clarification_questions(tool_name, missing_fields)
                        if questions:
                            clarification_msg = f"Thanks! I still need a bit more information:\n\n"
                            clarification_msg += "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
                            
                            yield create_stream_event(
                                "clarification_needed",
                                {
                                    "agent_name": agent_name,
                                    "message": clarification_msg,
                                    "questions": questions,
                                    "context": {
                                        "original_prompt": original_prompt,
                                        "agent": agent_name,
                                        "tool_name": tool_name,
                                        "extracted_entities": merged_entities,
                                        "missing_fields": missing_fields,
                                    },
                                },
                            )
                            
                            yield create_stream_event(
                                "complete",
                                {"message": "Waiting for additional information", "needs_clarification": True}
                            )
                            return
                
                # All fields present - combine message with context and proceed
                combined_message = (
                    f"[Original request: {original_prompt}]\n\n"
                    f"[User provided: {request.message}]\n\n"
                    f"[Extracted info: {merged_entities}]\n\n"
                    f"Please proceed with the {tool_name} tool using the extracted info."
                )
                state.user_message = combined_message
                state.extracted_entities = merged_entities
                state.inferred_action = tool_name
                
                yield create_stream_event(
                    "routing",
                    {
                        "agents": target_agents,
                        "message": f"Continuing with {agent_name} agent",
                    },
                )
                state.target_agents = target_agents
            else:
                # Fall back to normal classification
                clarification_context = None

        if not clarification_context:
            # Normal flow: Classification
            yield create_stream_event(
                "classification",
                {"message": "Analyzing request...", "request_id": request_id},
            )

            classification_result, target_agents = await stream_classification(state)
            state.target_agents = target_agents

            # Log classification result
            await history_repo.record_classification(
                request_id=request_id,
                target_agents=target_agents,
                classification_result=classification_result,
            )

            yield create_stream_event(
                "routing",
                {
                    "agents": target_agents,
                    "message": f"Routing to {len(target_agents)} agent(s)",
                },
            )
            
            # --- Pre-flight clarification check ---
            # Check if the inferred action requires fields that are missing
            inferred_action = state.inferred_action
            extracted_entities = state.extracted_entities
            
            # Map action to tool name
            tool_name = ACTION_TO_TOOL.get(inferred_action, inferred_action)
            
            if tool_name:
                missing_fields = get_missing_fields(tool_name, extracted_entities)
                
                if missing_fields:
                    questions = get_clarification_questions(tool_name, missing_fields)
                    
                    # Build clarification message
                    if questions:
                        agent_name = target_agents[0] if target_agents else "assistant"
                        clarification_msg = f"I can help with that. Please provide the following information:\n\n"
                        clarification_msg += "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
                        
                        # Emit clarification_needed event
                        yield create_stream_event(
                            "clarification_needed",
                            {
                                "agent_name": agent_name,
                                "message": clarification_msg,
                                "questions": questions,
                                "context": {
                                    "original_prompt": request.message,
                                    "agent": agent_name,
                                    "tool_name": tool_name,
                                    "extracted_entities": extracted_entities,
                                    "missing_fields": missing_fields,
                                },
                            },
                        )
                        
                        # Mark request as needing clarification
                        await history_repo.complete_request(
                            request_id,
                            completed_agents=[],
                            status="needs_clarification"
                        )
                        
                        yield create_stream_event(
                            "complete",
                            {"message": "Waiting for additional information", "needs_clarification": True}
                        )
                        return

        target_agents = state.target_agents

        if not target_agents:
            await history_repo.complete_request(request_id, completed_agents=[])
            yield create_stream_event("complete", {"message": "No agents needed", "results": []})
            return

        # Emit agent_start for all agents and log to database
        for agent in target_agents:
            await history_repo.start_agent(request_id, agent)
            yield create_stream_event(
                "agent_start",
                {"message": f"{agent.title()} agent starting..."},
                agent_name=agent,
            )

        # Run all agents in parallel
        result = await run_agents_parallel(state)

        # Track pending approvals
        pending_approval_ids: list[str] = []
        approval_repo = _get_approval_repo()

        # Emit results for each agent
        for agent_result in result.get("agent_results", []):
            # Log agent completion to database
            await history_repo.complete_agent(
                request_id=request_id,
                agent_name=agent_result.agent_name,
                message=agent_result.message,
                data=agent_result.data,
                tool_calls=agent_result.tool_calls,
                pending_actions=getattr(agent_result, 'pending_actions', None),
            )
            yield create_stream_event(
                "agent_complete",
                {
                    "status": agent_result.status,
                    "message": agent_result.message,
                    "data": agent_result.data,
                    "tool_calls": agent_result.tool_calls,
                },
                agent_name=agent_result.agent_name,
            )

            # Check if agent needs clarification from user
            needs_clarification = (
                getattr(agent_result, 'needs_clarification', False) or
                getattr(agent_result, 'status', '') == 'needs_clarification'
            )
            if needs_clarification:
                yield create_stream_event(
                    "clarification_needed",
                    {
                        "agent_name": agent_result.agent_name,
                        "message": agent_result.message,
                        "questions": getattr(agent_result, 'clarification_questions', []) or [],
                        "context": getattr(agent_result, 'clarification_context', {}) or {},
                    },
                )

            # Check for pending actions that require approval
            if hasattr(agent_result, 'pending_actions') and agent_result.pending_actions:
                for action in agent_result.pending_actions:
                    approval_id = str(uuid.uuid4())
                    approval_doc = ApprovalDocument.create_with_expiry(
                        approval_id=approval_id,
                        request_id=request_id,
                        agent_name=agent_result.agent_name,
                        action_type=action.get("action", "unknown"),
                        action_description=action.get("preview", "Action requires approval"),
                        action_data=action.get("args", {}),
                        expiry_hours=24,
                    )
                    # Save to database
                    await approval_repo.create(approval_doc)
                    pending_approval_ids.append(approval_id)

                    yield create_stream_event(
                        "approval_required",
                        {
                            "approval_id": approval_id,
                            "agent_name": agent_result.agent_name,
                            "action_type": action.get("action", "unknown"),
                            "description": action.get("preview", "Action requires approval"),
                            "args": action.get("args", {}),
                        },
                    )

        # Complete request in database
        await history_repo.complete_request(
            request_id=request_id,
            completed_agents=result.get("completed_agents", []),
            pending_approvals=pending_approval_ids if pending_approval_ids else None,
        )

        # Complete
        yield create_stream_event(
            "complete",
            {
                "message": "All agents completed",
                "request_id": request_id,
                "agents_invoked": result.get("completed_agents", []),
                "results": [r.model_dump() for r in result.get("agent_results", [])],
                "pending_approvals": pending_approval_ids,
            },
        )

    except Exception as e:
        logger.error(f"Parallel stream error: {e}")
        # Log error to database
        try:
            await history_repo.complete_request(request_id, completed_agents=[], error=str(e))
        except Exception:
            pass  # Don't fail on logging error
        yield create_stream_event("error", {"error": str(e), "request_id": request_id})


def create_event_stream(request: ChatRequest, parallel: bool = True, use_tasks: bool = False) -> EventSourceResponse:
    """Create an SSE response for streaming agent updates.

    Args:
        request: The chat request to process
        parallel: Whether to use parallel execution (default: True)
        use_tasks: Whether to use task-based orchestration (default: False)

    Returns:
        EventSourceResponse for SSE streaming
    """
    if use_tasks:
        generator = generate_events_task_based
    elif parallel:
        generator = generate_events_parallel
    else:
        generator = generate_events
    
    return EventSourceResponse(
        generator(request),
        media_type="text/event-stream",
    )


async def generate_events_task_based(request: ChatRequest) -> AsyncGenerator[str, None]:
    """Generate SSE events using task-based orchestration.

    This version:
    1. Uses the task planner to decompose the request
    2. Executes tasks with dependency-aware orchestration
    3. Streams detailed task progress events

    Args:
        request: The chat request to process

    Yields:
        SSE event strings in real-time
    """
    request_id = request.request_id or str(uuid.uuid4())
    history_repo = _get_history_repo()
    approval_repo = _get_approval_repo()

    logger.info(f"Starting task-based stream for request {request_id}")

    state = GraphState(
        request_id=request_id,
        user_message=request.message,
        context=request.context,
        org_id=request.context.get("org_id", "default") if request.context else "default",
    )

    try:
        # Log request start
        await history_repo.start_request(
            request_id=request_id,
            user_message=request.message,
            event_name=request.event_name,
            context=request.context,
        )

        # Step 1: Task Planning
        yield create_stream_event(
            "planning",
            {"message": "Analyzing and planning tasks...", "request_id": request_id},
        )

        plan_result = await plan_tasks(state)
        task_plan = plan_result.get("task_plan")
        target_agents = plan_result.get("target_agents", [])

        if not task_plan or not task_plan.tasks:
            yield create_stream_event(
                "routing",
                {
                    "agents": [],
                    "message": "No tasks were generated for this request",
                },
            )
            await history_repo.complete_request(request_id, completed_agents=[])
            yield create_stream_event("complete", {"message": "No tasks needed", "results": []})
            return

        # Emit task plan event with breakdown
        yield create_stream_event(
            "task_plan",
            {
                "plan_id": task_plan.plan_id,
                "request_type": task_plan.request_type,
                "total_tasks": len(task_plan.tasks),
                "execution_strategy": task_plan.execution_strategy,
                "target_agents": target_agents,
                "tasks": [
                    {
                        "id": t.id,
                        "agent": t.agent,
                        "action": t.action,
                        "description": t.description,
                        "depends_on": t.depends_on,
                        "requires_approval": t.requires_approval,
                    }
                    for t in task_plan.tasks
                ],
                "extracted_entities": [
                    {"type": e.entity_type, "value": e.value}
                    for e in task_plan.extracted_entities
                ],
            },
        )

        yield create_stream_event(
            "routing",
            {
                "agents": target_agents,
                "message": f"Executing {len(task_plan.tasks)} task(s) with {len(target_agents)} agent(s)",
            },
        )

        # Update state with task plan
        state.task_plan = task_plan
        state.target_agents = target_agents

        # Track pending approvals
        pending_approval_ids: list[str] = []

        # Step 2: Execute tasks with orchestration
        async for task_event in orchestrate_with_events(task_plan, state):
            # Convert task events to SSE stream events
            event_type = task_event.event_type
            
            if event_type == "plan_start":
                yield create_stream_event(
                    "orchestration_start",
                    task_event.data,
                )
            
            elif event_type == "task_start":
                agent_name = task_event.data.get("agent", "unknown")
                yield create_stream_event(
                    "task_start",
                    {
                        "task_id": task_event.task_id,
                        "agent": agent_name,
                        "action": task_event.data.get("action"),
                        "description": task_event.data.get("description"),
                    },
                    agent_name=agent_name,
                )
            
            elif event_type == "task_complete":
                agent_name = task_event.task.agent if task_event.task else "unknown"
                yield create_stream_event(
                    "task_complete",
                    {
                        "task_id": task_event.task_id,
                        "status": "success",
                        "message": task_event.data.get("message"),
                        "result": task_event.data.get("result"),
                        "execution_time": task_event.data.get("execution_time"),
                    },
                    agent_name=agent_name,
                )
            
            elif event_type == "task_failed":
                agent_name = task_event.task.agent if task_event.task else "unknown"
                yield create_stream_event(
                    "task_failed",
                    {
                        "task_id": task_event.task_id,
                        "status": "error",
                        "error": task_event.data.get("error"),
                        "execution_time": task_event.data.get("execution_time"),
                    },
                    agent_name=agent_name,
                )
            
            elif event_type == "task_approval_required":
                # Create approval record
                approval_id = str(uuid.uuid4())
                agent_name = task_event.data.get("agent", "unknown")
                
                approval_doc = ApprovalDocument.create_with_expiry(
                    approval_id=approval_id,
                    request_id=request_id,
                    agent_name=agent_name,
                    action_type=task_event.data.get("action", "unknown"),
                    action_description=task_event.data.get("description", "Action requires approval"),
                    action_data=task_event.data.get("parameters", {}),
                    expiry_hours=24,
                )
                await approval_repo.create(approval_doc)
                pending_approval_ids.append(approval_id)
                
                yield create_stream_event(
                    "approval_required",
                    {
                        "approval_id": approval_id,
                        "task_id": task_event.task_id,
                        "agent_name": agent_name,
                        "action_type": task_event.data.get("action"),
                        "description": task_event.data.get("description"),
                        "parameters": task_event.data.get("parameters"),
                    },
                )
            
            elif event_type == "plan_complete":
                yield create_stream_event(
                    "orchestration_complete",
                    {
                        "completed": task_event.data.get("completed", 0),
                        "failed": task_event.data.get("failed", 0),
                        "skipped": task_event.data.get("skipped", 0),
                    },
                )

        # Complete request in database
        await history_repo.complete_request(
            request_id=request_id,
            completed_agents=target_agents,
            pending_approvals=pending_approval_ids if pending_approval_ids else None,
        )

        # Final complete event
        yield create_stream_event(
            "complete",
            {
                "message": "All tasks completed",
                "request_id": request_id,
                "plan_id": task_plan.plan_id,
                "agents_invoked": target_agents,
                "pending_approvals": pending_approval_ids,
            },
        )

    except Exception as e:
        logger.error(f"Task-based stream error: {e}")
        try:
            await history_repo.complete_request(request_id, completed_agents=[], error=str(e))
        except Exception:
            pass
        yield create_stream_event("error", {"error": str(e), "request_id": request_id})


async def get_pending_approval(approval_id: str) -> Optional[ApprovalDocument]:
    """Get a pending approval by ID from the database."""
    approval_repo = _get_approval_repo()
    return await approval_repo.find_by_approval_id(approval_id)


async def get_all_pending_approvals() -> list[ApprovalDocument]:
    """Get all pending approvals from the database."""
    approval_repo = _get_approval_repo()
    return await approval_repo.find_pending()


async def update_approval_status(
    approval_id: str,
    status: str,
    changed_by: Optional[str] = None,
    reason: Optional[str] = None,
    edits: Optional[dict] = None,
    execution_result: Optional[dict] = None,
) -> Optional[ApprovalDocument]:
    """Update the status of an approval in the database."""
    approval_repo = _get_approval_repo()
    return await approval_repo.update_status(
        approval_id=approval_id,
        new_status=status,
        changed_by=changed_by,
        reason=reason,
        edits=edits,
        execution_result=execution_result,
    )


async def delete_approval(approval_id: str) -> bool:
    """Delete an approval from the database."""
    approval_repo = _get_approval_repo()
    approval = await approval_repo.find_by_approval_id(approval_id)
    if approval and approval.id:
        return await approval_repo.delete_by_id(approval.id)
    return False


async def expire_old_approvals() -> int:
    """Expire approvals that have passed their expiry time."""
    approval_repo = _get_approval_repo()
    return await approval_repo.expire_old_approvals()
