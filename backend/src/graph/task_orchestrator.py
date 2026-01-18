"""Task Orchestrator for dependency-aware task execution.

This module orchestrates the execution of tasks from a TaskPlan,
respecting dependencies and enabling parallel execution when possible.

Key features:
- Dependency-aware execution (tasks wait for their dependencies)
- Parallel execution of independent tasks
- Progress streaming via callback
- Approval handling for sensitive actions
- Graceful failure handling (skip dependent tasks on failure)
"""

import asyncio
import logging
import time
from typing import AsyncGenerator, Callable, Optional, Any
from datetime import datetime

from src.models.task_plan import TaskPlan, Task
from src.models.state import GraphState, AgentResult

logger = logging.getLogger(__name__)


class TaskExecutionResult:
    """Result of executing a single task."""
    
    def __init__(
        self,
        task_id: str,
        success: bool,
        message: str,
        data: Optional[dict] = None,
        error: Optional[str] = None,
        execution_time: float = 0.0,
        requires_approval: bool = False,
        approval_data: Optional[dict] = None,
    ):
        self.task_id = task_id
        self.success = success
        self.message = message
        self.data = data or {}
        self.error = error
        self.execution_time = execution_time
        self.requires_approval = requires_approval
        self.approval_data = approval_data


class TaskEvent:
    """Event emitted during task execution for streaming."""
    
    def __init__(
        self,
        event_type: str,
        task_id: str,
        task: Optional[Task] = None,
        data: Optional[dict] = None,
        timestamp: Optional[datetime] = None,
    ):
        self.event_type = event_type
        self.task_id = task_id
        self.task = task
        self.data = data or {}
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert event to dictionary for SSE."""
        return {
            "event_type": self.event_type,
            "task_id": self.task_id,
            "task": {
                "id": self.task.id,
                "agent": self.task.agent,
                "action": self.task.action,
                "description": self.task.description,
                "status": self.task.status,
                "depends_on": self.task.depends_on,
                "requires_approval": self.task.requires_approval,
            } if self.task else None,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
        }


# Type alias for event callback
EventCallback = Callable[[TaskEvent], Any]


class TaskOrchestrator:
    """Orchestrates task execution with dependency management.
    
    The orchestrator:
    1. Takes a TaskPlan with tasks and dependencies
    2. Executes tasks in the correct order
    3. Runs independent tasks in parallel
    4. Handles failures by skipping dependent tasks
    5. Emits events for real-time progress streaming
    """
    
    def __init__(
        self,
        task_executor: "TaskExecutor",
        event_callback: Optional[EventCallback] = None,
    ):
        """Initialize the orchestrator.
        
        Args:
            task_executor: Executor that runs individual tasks
            event_callback: Optional callback for streaming events
        """
        self.executor = task_executor
        self.event_callback = event_callback
        self.completed_task_ids: set[str] = set()
        self.failed_task_ids: set[str] = set()
        self.task_results: dict[str, TaskExecutionResult] = {}
    
    async def _emit_event(self, event: TaskEvent) -> None:
        """Emit an event through the callback if set."""
        if self.event_callback:
            result = self.event_callback(event)
            if asyncio.iscoroutine(result):
                await result
    
    async def execute_plan(
        self,
        plan: TaskPlan,
        state: GraphState,
    ) -> dict[str, TaskExecutionResult]:
        """Execute all tasks in a plan respecting dependencies.
        
        Args:
            plan: The TaskPlan to execute
            state: Current graph state with context
            
        Returns:
            Dictionary mapping task IDs to their results
        """
        logger.info(f"Starting execution of plan {plan.plan_id} with {len(plan.tasks)} tasks")
        
        # Reset state
        self.completed_task_ids = set()
        self.failed_task_ids = set()
        self.task_results = {}
        
        # Emit plan start event
        await self._emit_event(TaskEvent(
            event_type="plan_start",
            task_id=plan.plan_id,
            data={
                "total_tasks": len(plan.tasks),
                "execution_strategy": plan.execution_strategy,
                "target_agents": plan.target_agents,
            },
        ))
        
        # Execute based on strategy
        if plan.execution_strategy == "sequential":
            await self._execute_sequential(plan, state)
        elif plan.execution_strategy == "parallel":
            await self._execute_parallel(plan, state)
        else:  # mixed
            await self._execute_mixed(plan, state)
        
        # Emit plan complete event
        successful = len(self.completed_task_ids)
        failed = len(self.failed_task_ids)
        skipped = len(plan.tasks) - successful - failed
        
        await self._emit_event(TaskEvent(
            event_type="plan_complete",
            task_id=plan.plan_id,
            data={
                "completed": successful,
                "failed": failed,
                "skipped": skipped,
                "results": {tid: r.message for tid, r in self.task_results.items()},
            },
        ))
        
        logger.info(f"Plan {plan.plan_id} complete: {successful} completed, {failed} failed, {skipped} skipped")
        
        return self.task_results
    
    async def _execute_sequential(self, plan: TaskPlan, state: GraphState) -> None:
        """Execute all tasks sequentially."""
        for task in plan.tasks:
            if task.id in self.failed_task_ids:
                continue
                
            # Check if dependencies are satisfied
            if not self._can_execute(task):
                self._skip_task(task, "Dependencies not met or failed")
                continue
            
            await self._execute_task(task, state)
    
    async def _execute_parallel(self, plan: TaskPlan, state: GraphState) -> None:
        """Execute all tasks in parallel (ignoring dependencies)."""
        tasks = [self._execute_task(task, state) for task in plan.tasks]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_mixed(self, plan: TaskPlan, state: GraphState) -> None:
        """Execute tasks respecting dependencies, parallelizing when possible.
        
        This is the main execution mode that:
        1. Finds all tasks whose dependencies are satisfied
        2. Runs them in parallel
        3. Repeats until all tasks are done or no more can run
        """
        max_iterations = len(plan.tasks) + 1  # Safety limit
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Find tasks ready to execute
            ready_tasks = self._get_ready_tasks(plan)
            
            if not ready_tasks:
                # Check if we're done or stuck
                remaining = [
                    t for t in plan.tasks
                    if t.id not in self.completed_task_ids
                    and t.id not in self.failed_task_ids
                    and t.status != "skipped"
                ]
                
                if not remaining:
                    break  # All done
                
                # Mark remaining tasks as skipped (dependencies failed)
                for task in remaining:
                    self._skip_task(task, "Dependencies could not be satisfied")
                break
            
            logger.info(f"Iteration {iteration}: executing {len(ready_tasks)} tasks in parallel")
            
            # Execute ready tasks in parallel
            await asyncio.gather(*[
                self._execute_task(task, state) for task in ready_tasks
            ], return_exceptions=True)
    
    def _get_ready_tasks(self, plan: TaskPlan) -> list[Task]:
        """Get tasks that are ready to execute.
        
        A task is ready if:
        1. It's not already completed or failed
        2. All its dependencies are completed (not failed)
        """
        ready = []
        for task in plan.tasks:
            # Skip already processed tasks
            if task.id in self.completed_task_ids:
                continue
            if task.id in self.failed_task_ids:
                continue
            if task.status == "skipped":
                continue
            if task.status == "running":
                continue
            
            # Check dependencies
            if self._can_execute(task):
                ready.append(task)
        
        return ready
    
    def _can_execute(self, task: Task) -> bool:
        """Check if a task can be executed.
        
        Returns True if all dependencies are completed successfully.
        """
        for dep_id in task.depends_on:
            if dep_id not in self.completed_task_ids:
                return False
            if dep_id in self.failed_task_ids:
                return False
        return True
    
    def _skip_task(self, task: Task, reason: str) -> None:
        """Mark a task as skipped."""
        task.mark_skipped(reason)
        self.task_results[task.id] = TaskExecutionResult(
            task_id=task.id,
            success=False,
            message=f"Skipped: {reason}",
            error=reason,
        )
        logger.info(f"Task {task.id} skipped: {reason}")
    
    async def _execute_task(self, task: Task, state: GraphState) -> None:
        """Execute a single task.
        
        Args:
            task: The task to execute
            state: Current graph state
        """
        task_start = time.time()
        task.mark_running()
        
        # Emit task start event
        await self._emit_event(TaskEvent(
            event_type="task_start",
            task_id=task.id,
            task=task,
            data={
                "agent": task.agent,
                "action": task.action,
                "description": task.description,
            },
        ))
        
        try:
            # Check if task requires approval
            if task.requires_approval:
                await self._handle_approval_task(task, state)
            else:
                # Execute the task
                result = await self.executor.execute_task(task, state)
                
                execution_time = time.time() - task_start
                
                if result.success:
                    task.mark_completed(result.data)
                    self.completed_task_ids.add(task.id)
                    
                    # Emit task complete event
                    await self._emit_event(TaskEvent(
                        event_type="task_complete",
                        task_id=task.id,
                        task=task,
                        data={
                            "message": result.message,
                            "result": result.data,
                            "execution_time": execution_time,
                        },
                    ))
                else:
                    task.mark_failed(result.error or "Unknown error")
                    self.failed_task_ids.add(task.id)
                    
                    # Emit task failed event
                    await self._emit_event(TaskEvent(
                        event_type="task_failed",
                        task_id=task.id,
                        task=task,
                        data={
                            "error": result.error,
                            "execution_time": execution_time,
                        },
                    ))
                
                result.execution_time = execution_time
                self.task_results[task.id] = result
                
        except Exception as e:
            execution_time = time.time() - task_start
            error_msg = str(e)
            
            task.mark_failed(error_msg)
            self.failed_task_ids.add(task.id)
            
            self.task_results[task.id] = TaskExecutionResult(
                task_id=task.id,
                success=False,
                message=f"Task failed with exception",
                error=error_msg,
                execution_time=execution_time,
            )
            
            # Emit task error event
            await self._emit_event(TaskEvent(
                event_type="task_error",
                task_id=task.id,
                task=task,
                data={
                    "error": error_msg,
                    "execution_time": execution_time,
                },
            ))
            
            logger.error(f"Task {task.id} failed with exception: {e}")
    
    async def _handle_approval_task(self, task: Task, state: GraphState) -> None:
        """Handle a task that requires approval.
        
        Instead of executing immediately, we:
        1. Generate a preview/draft of what would happen
        2. Mark it as pending approval
        3. Emit an approval_required event
        """
        # Emit approval required event
        await self._emit_event(TaskEvent(
            event_type="task_approval_required",
            task_id=task.id,
            task=task,
            data={
                "agent": task.agent,
                "action": task.action,
                "parameters": task.parameters,
                "description": task.description,
            },
        ))
        
        # Mark task as completed but with approval required
        # The actual execution will happen when approval is granted
        self.task_results[task.id] = TaskExecutionResult(
            task_id=task.id,
            success=True,
            message="Awaiting approval",
            requires_approval=True,
            approval_data={
                "agent": task.agent,
                "action": task.action,
                "parameters": task.parameters,
                "description": task.description,
            },
        )
        
        # Consider the task "completed" for dependency purposes
        # so dependent tasks can proceed
        task.mark_completed({"status": "pending_approval"})
        self.completed_task_ids.add(task.id)


class TaskExecutor:
    """Executes individual tasks by routing to appropriate agents.
    
    This class bridges the gap between the TaskPlan's declarative tasks
    and the actual agent execution.
    """
    
    def __init__(self):
        """Initialize the task executor."""
        self._agent_runners = {}
        self._load_agent_runners()
    
    def _load_agent_runners(self):
        """Load agent runner functions from the workflow module."""
        from src.graph.workflow import AGENT_RUNNERS
        self._agent_runners = AGENT_RUNNERS
    
    async def execute_task(self, task: Task, state: GraphState) -> TaskExecutionResult:
        """Execute a single task using the appropriate agent.
        
        Args:
            task: The task to execute
            state: Current graph state
            
        Returns:
            TaskExecutionResult with execution outcome
        """
        agent_name = task.agent
        
        if agent_name not in self._agent_runners:
            return TaskExecutionResult(
                task_id=task.id,
                success=False,
                message=f"Agent {agent_name} not found",
                error=f"Unknown agent: {agent_name}",
            )
        
        logger.info(f"Executing task {task.id} with agent {agent_name}: {task.action}")
        
        try:
            # Create a task-specific prompt from the task parameters
            task_prompt = self._build_task_prompt(task)
            
            # Create a modified state with the task-specific prompt
            task_state = GraphState(
                request_id=state.request_id,
                user_message=task_prompt,
                context=state.context,
                org_id=state.org_id,
                task_plan=state.task_plan,
                current_task_id=task.id,
            )
            
            # Run the agent
            runner = self._agent_runners[agent_name]
            result = await runner(task_state)
            
            # Extract agent result
            agent_results = result.get("agent_results", [])
            if agent_results:
                agent_result = agent_results[0]
                return TaskExecutionResult(
                    task_id=task.id,
                    success=agent_result.status == "success",
                    message=agent_result.message,
                    data=agent_result.data,
                    error=agent_result.message if agent_result.status == "error" else None,
                )
            
            return TaskExecutionResult(
                task_id=task.id,
                success=False,
                message="No result from agent",
                error="Agent returned no results",
            )
            
        except Exception as e:
            logger.error(f"Task {task.id} execution error: {e}")
            return TaskExecutionResult(
                task_id=task.id,
                success=False,
                message=f"Execution failed: {str(e)}",
                error=str(e),
            )
    
    def _build_task_prompt(self, task: Task) -> str:
        """Build a prompt for the agent from the task.
        
        This creates a clear, actionable prompt that tells the agent
        exactly what to do with what parameters.
        
        Args:
            task: The task to build a prompt for
            
        Returns:
            A prompt string for the agent
        """
        # Build a structured prompt from task details
        prompt_parts = [
            f"Execute the following action: {task.action}",
            f"\nDescription: {task.description}",
        ]
        
        if task.parameters:
            prompt_parts.append("\nParameters:")
            for key, value in task.parameters.items():
                prompt_parts.append(f"  - {key}: {value}")
        
        prompt_parts.append("\nExecute this action using the appropriate tool.")
        
        return "\n".join(prompt_parts)


# Convenience function to create and run the orchestrator
async def orchestrate_task_plan(
    plan: TaskPlan,
    state: GraphState,
    event_callback: Optional[EventCallback] = None,
) -> dict[str, TaskExecutionResult]:
    """Orchestrate execution of a task plan.
    
    Convenience function that creates an orchestrator and executor,
    then runs the plan.
    
    Args:
        plan: The TaskPlan to execute
        state: Current graph state
        event_callback: Optional callback for streaming events
        
    Returns:
        Dictionary mapping task IDs to their results
    """
    executor = TaskExecutor()
    orchestrator = TaskOrchestrator(executor, event_callback)
    return await orchestrator.execute_plan(plan, state)


async def orchestrate_with_events(
    plan: TaskPlan,
    state: GraphState,
) -> AsyncGenerator[TaskEvent, None]:
    """Orchestrate execution and yield events as a generator.
    
    This is useful for SSE streaming where you want to yield events
    as they occur.
    
    Args:
        plan: The TaskPlan to execute
        state: Current graph state
        
    Yields:
        TaskEvent objects as they occur
    """
    event_queue: asyncio.Queue[TaskEvent] = asyncio.Queue()
    
    async def queue_callback(event: TaskEvent):
        await event_queue.put(event)
    
    # Start orchestration in background task
    async def run_orchestration():
        executor = TaskExecutor()
        orchestrator = TaskOrchestrator(executor, queue_callback)
        await orchestrator.execute_plan(plan, state)
        # Signal completion with None
        await event_queue.put(None)
    
    orchestration_task = asyncio.create_task(run_orchestration())
    
    try:
        while True:
            event = await event_queue.get()
            if event is None:
                break
            yield event
    finally:
        orchestration_task.cancel()
        try:
            await orchestration_task
        except asyncio.CancelledError:
            pass
