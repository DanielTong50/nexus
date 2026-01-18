"""
Phase 3 Orchestrator Tests

Comprehensive tests for:
1. Task orchestrator dependency management
2. Parallel and sequential execution
3. Failure handling and task skipping
4. Event emission for streaming
5. Task executor integration

Run with: pytest tests/test_phase3_orchestrator.py -v
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime


# =============================================================================
# TASK ORCHESTRATOR TESTS
# =============================================================================

class TestTaskOrchestrator:
    """Tests for the TaskOrchestrator class."""
    
    @pytest.mark.asyncio
    async def test_execute_sequential_plan(self):
        """Test executing tasks sequentially."""
        from src.graph.task_orchestrator import TaskOrchestrator, TaskExecutor, TaskExecutionResult
        from src.models.task_plan import TaskPlan, Task
        from src.models.state import GraphState
        
        # Create a simple sequential plan
        tasks = [
            Task(id="t1", agent="partnerships", action="log", parameters={}, description="Task 1"),
            Task(id="t2", agent="events", action="notify", parameters={}, description="Task 2", depends_on=["t1"]),
            Task(id="t3", agent="finance", action="invoice", parameters={}, description="Task 3", depends_on=["t2"]),
        ]
        
        plan = TaskPlan(
            plan_id="test_plan",
            request_id="test_req",
            tasks=tasks,
            execution_strategy="sequential",
        )
        
        # Mock executor
        mock_executor = MagicMock(spec=TaskExecutor)
        mock_executor.execute_task = AsyncMock(return_value=TaskExecutionResult(
            task_id="",
            success=True,
            message="Success",
            data={"result": "ok"},
        ))
        
        # Track events
        events = []
        async def track_event(event):
            events.append(event.event_type)
        
        orchestrator = TaskOrchestrator(mock_executor, track_event)
        state = GraphState(request_id="test_req", user_message="test")
        
        results = await orchestrator.execute_plan(plan, state)
        
        # All tasks should complete
        assert len(results) == 3
        assert all(r.success for r in results.values())
        
        # Should have plan_start, task events, plan_complete
        assert "plan_start" in events
        assert "plan_complete" in events
        assert events.count("task_start") == 3
        assert events.count("task_complete") == 3
    
    @pytest.mark.asyncio
    async def test_execute_parallel_independent_tasks(self):
        """Test that independent tasks run in parallel."""
        from src.graph.task_orchestrator import TaskOrchestrator, TaskExecutor, TaskExecutionResult
        from src.models.task_plan import TaskPlan, Task
        from src.models.state import GraphState
        
        # Create tasks with no dependencies (all parallel)
        tasks = [
            Task(id="t1", agent="partnerships", action="log", parameters={}, description="Task 1"),
            Task(id="t2", agent="events", action="notify", parameters={}, description="Task 2"),
            Task(id="t3", agent="finance", action="invoice", parameters={}, description="Task 3"),
        ]
        
        plan = TaskPlan(
            plan_id="test_plan",
            request_id="test_req",
            tasks=tasks,
            execution_strategy="mixed",
        )
        
        # Track execution order with delay to verify parallelism
        execution_order = []
        
        async def mock_execute(task, state):
            execution_order.append(f"start_{task.id}")
            await asyncio.sleep(0.05)  # Small delay
            execution_order.append(f"end_{task.id}")
            return TaskExecutionResult(
                task_id=task.id,
                success=True,
                message="Success",
            )
        
        mock_executor = MagicMock(spec=TaskExecutor)
        mock_executor.execute_task = mock_execute
        
        orchestrator = TaskOrchestrator(mock_executor)
        state = GraphState(request_id="test_req", user_message="test")
        
        results = await orchestrator.execute_plan(plan, state)
        
        # All should complete
        assert len(results) == 3
        
        # For parallel execution, all starts should come before all ends
        starts = [e for e in execution_order if e.startswith("start")]
        ends = [e for e in execution_order if e.startswith("end")]
        
        # In parallel mode, tasks start together
        # The first 3 entries should all be starts (in mixed strategy)
        assert len(starts) == 3
        assert len(ends) == 3
    
    @pytest.mark.asyncio
    async def test_dependency_chain_execution(self):
        """Test that dependencies are respected in execution order."""
        from src.graph.task_orchestrator import TaskOrchestrator, TaskExecutor, TaskExecutionResult
        from src.models.task_plan import TaskPlan, Task
        from src.models.state import GraphState
        
        # Create a dependency chain: t1 -> t2 -> t3
        tasks = [
            Task(id="t1", agent="partnerships", action="log", parameters={}, description="Task 1"),
            Task(id="t2", agent="events", action="notify", parameters={}, description="Task 2", depends_on=["t1"]),
            Task(id="t3", agent="finance", action="invoice", parameters={}, description="Task 3", depends_on=["t2"]),
        ]
        
        plan = TaskPlan(
            plan_id="test_plan",
            request_id="test_req",
            tasks=tasks,
            execution_strategy="mixed",
        )
        
        # Track completion order
        completion_order = []
        
        async def mock_execute(task, state):
            completion_order.append(task.id)
            return TaskExecutionResult(
                task_id=task.id,
                success=True,
                message="Success",
            )
        
        mock_executor = MagicMock(spec=TaskExecutor)
        mock_executor.execute_task = mock_execute
        
        orchestrator = TaskOrchestrator(mock_executor)
        state = GraphState(request_id="test_req", user_message="test")
        
        await orchestrator.execute_plan(plan, state)
        
        # Order should be t1 -> t2 -> t3
        assert completion_order == ["t1", "t2", "t3"]
    
    @pytest.mark.asyncio
    async def test_fan_out_parallel_execution(self):
        """Test fan-out pattern: one task followed by multiple parallel tasks."""
        from src.graph.task_orchestrator import TaskOrchestrator, TaskExecutor, TaskExecutionResult
        from src.models.task_plan import TaskPlan, Task
        from src.models.state import GraphState
        
        # t1 -> [t2, t3, t4] (fan-out)
        tasks = [
            Task(id="t1", agent="partnerships", action="log", parameters={}, description="Log"),
            Task(id="t2", agent="events", action="notify1", parameters={}, description="Notify 1", depends_on=["t1"]),
            Task(id="t3", agent="events", action="notify2", parameters={}, description="Notify 2", depends_on=["t1"]),
            Task(id="t4", agent="finance", action="invoice", parameters={}, description="Invoice", depends_on=["t1"]),
        ]
        
        plan = TaskPlan(
            plan_id="test_plan",
            request_id="test_req",
            tasks=tasks,
            execution_strategy="mixed",
        )
        
        execution_batches = []
        current_batch = []
        
        async def mock_execute(task, state):
            current_batch.append(task.id)
            return TaskExecutionResult(task_id=task.id, success=True, message="Success")
        
        mock_executor = MagicMock(spec=TaskExecutor)
        mock_executor.execute_task = mock_execute
        
        orchestrator = TaskOrchestrator(mock_executor)
        state = GraphState(request_id="test_req", user_message="test")
        
        await orchestrator.execute_plan(plan, state)
        
        # All 4 tasks should complete
        assert len(orchestrator.completed_task_ids) == 4
    
    @pytest.mark.asyncio
    async def test_task_failure_skips_dependents(self):
        """Test that dependent tasks are skipped when a task fails."""
        from src.graph.task_orchestrator import TaskOrchestrator, TaskExecutor, TaskExecutionResult
        from src.models.task_plan import TaskPlan, Task
        from src.models.state import GraphState
        
        tasks = [
            Task(id="t1", agent="partnerships", action="log", parameters={}, description="Task 1"),
            Task(id="t2", agent="events", action="notify", parameters={}, description="Task 2", depends_on=["t1"]),
            Task(id="t3", agent="finance", action="invoice", parameters={}, description="Task 3", depends_on=["t2"]),
        ]
        
        plan = TaskPlan(
            plan_id="test_plan",
            request_id="test_req",
            tasks=tasks,
            execution_strategy="mixed",
        )
        
        # t1 succeeds, t2 fails
        call_count = [0]
        
        async def mock_execute(task, state):
            call_count[0] += 1
            if task.id == "t1":
                return TaskExecutionResult(task_id=task.id, success=True, message="Success")
            elif task.id == "t2":
                return TaskExecutionResult(task_id=task.id, success=False, message="Failed", error="Test error")
            else:
                return TaskExecutionResult(task_id=task.id, success=True, message="Success")
        
        mock_executor = MagicMock(spec=TaskExecutor)
        mock_executor.execute_task = mock_execute
        
        orchestrator = TaskOrchestrator(mock_executor)
        state = GraphState(request_id="test_req", user_message="test")
        
        results = await orchestrator.execute_plan(plan, state)
        
        # t1 completed, t2 failed, t3 should be skipped (never executed)
        assert "t1" in orchestrator.completed_task_ids
        assert "t2" in orchestrator.failed_task_ids
        assert "t3" not in orchestrator.completed_task_ids
        assert "t3" not in orchestrator.failed_task_ids
        
        # t3 should be skipped, so only t1 and t2 were actually executed
        assert call_count[0] == 2
        
        # t3 should have a skip result
        assert results["t3"].success is False
        assert "Skipped" in results["t3"].message
    
    @pytest.mark.asyncio
    async def test_approval_required_task(self):
        """Test handling of tasks that require approval."""
        from src.graph.task_orchestrator import TaskOrchestrator, TaskExecutor, TaskExecutionResult
        from src.models.task_plan import TaskPlan, Task
        from src.models.state import GraphState
        
        tasks = [
            Task(id="t1", agent="partnerships", action="log", parameters={}, description="Log"),
            Task(
                id="t2", 
                agent="finance", 
                action="generate_invoice", 
                parameters={"amount": 1500}, 
                description="Create invoice",
                requires_approval=True,
            ),
        ]
        
        plan = TaskPlan(
            plan_id="test_plan",
            request_id="test_req",
            tasks=tasks,
            execution_strategy="sequential",
        )
        
        events = []
        async def track_event(event):
            events.append(event)
        
        async def mock_execute(task, state):
            return TaskExecutionResult(task_id=task.id, success=True, message="Success")
        
        mock_executor = MagicMock(spec=TaskExecutor)
        mock_executor.execute_task = mock_execute
        
        orchestrator = TaskOrchestrator(mock_executor, track_event)
        state = GraphState(request_id="test_req", user_message="test")
        
        results = await orchestrator.execute_plan(plan, state)
        
        # t2 should have approval required
        assert results["t2"].requires_approval is True
        
        # Should have emitted approval_required event
        approval_events = [e for e in events if e.event_type == "task_approval_required"]
        assert len(approval_events) == 1
        assert approval_events[0].task_id == "t2"


# =============================================================================
# TASK EXECUTOR TESTS
# =============================================================================

class TestTaskExecutor:
    """Tests for the TaskExecutor class."""
    
    @pytest.mark.asyncio
    async def test_execute_task_with_agent(self):
        """Test executing a task through an agent."""
        from src.graph.task_orchestrator import TaskExecutor, TaskExecutionResult
        from src.models.task_plan import Task
        from src.models.state import GraphState, AgentResult
        
        task = Task(
            id="t1",
            agent="partnerships",
            action="add_partnership",
            parameters={"company": "Google", "status": "Confirmed"},
            description="Add Google as sponsor",
        )
        
        state = GraphState(request_id="test_req", user_message="test")
        
        # Mock the agent runner
        mock_agent_result = AgentResult(
            agent_name="partnerships",
            status="success",
            message="Added Google successfully",
            data={"company": "Google"},
        )
        
        mock_runner = AsyncMock(return_value={
            "agent_results": [mock_agent_result],
            "completed_agents": ["partnerships"],
        })
        
        # Create executor and manually set the runners (bypassing _load_agent_runners)
        with patch.object(TaskExecutor, '_load_agent_runners'):
            executor = TaskExecutor()
            executor._agent_runners = {'partnerships': mock_runner}
            
            result = await executor.execute_task(task, state)
        
        assert result.success is True
        assert "Google" in result.message
    
    @pytest.mark.asyncio
    async def test_execute_task_unknown_agent(self):
        """Test executing a task with unknown agent."""
        from src.graph.task_orchestrator import TaskExecutor
        from src.models.task_plan import Task
        from src.models.state import GraphState
        
        task = Task(
            id="t1",
            agent="unknown_agent",
            action="do_something",
            parameters={},
            description="Unknown task",
        )
        
        state = GraphState(request_id="test_req", user_message="test")
        
        # Create executor with empty runners
        with patch.object(TaskExecutor, '_load_agent_runners'):
            executor = TaskExecutor()
            executor._agent_runners = {}  # Empty runners
            
            result = await executor.execute_task(task, state)
        
        assert result.success is False
        assert "not found" in result.message.lower() or "unknown" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_execute_task_agent_returns_error(self):
        """Test executing a task when agent returns an error."""
        from src.graph.task_orchestrator import TaskExecutor, TaskExecutionResult
        from src.models.task_plan import Task
        from src.models.state import GraphState, AgentResult
        
        task = Task(
            id="t1",
            agent="partnerships",
            action="add_partnership",
            parameters={"company": "Google"},
            description="Add Google",
        )
        
        state = GraphState(request_id="test_req", user_message="test")
        
        # Mock agent returning error
        mock_agent_result = AgentResult(
            agent_name="partnerships",
            status="error",
            message="Failed to add partnership: API error",
            data={},
        )
        
        mock_runner = AsyncMock(return_value={
            "agent_results": [mock_agent_result],
            "completed_agents": ["partnerships"],
        })
        
        with patch.object(TaskExecutor, '_load_agent_runners'):
            executor = TaskExecutor()
            executor._agent_runners = {'partnerships': mock_runner}
            
            result = await executor.execute_task(task, state)
        
        assert result.success is False
        assert "Failed" in result.message or "error" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_execute_task_agent_throws_exception(self):
        """Test executing a task when agent throws an exception."""
        from src.graph.task_orchestrator import TaskExecutor
        from src.models.task_plan import Task
        from src.models.state import GraphState
        
        task = Task(
            id="t1",
            agent="partnerships",
            action="add_partnership",
            parameters={},
            description="Add partner",
        )
        
        state = GraphState(request_id="test_req", user_message="test")
        
        # Mock agent that throws exception
        mock_runner = AsyncMock(side_effect=Exception("Connection timeout"))
        
        with patch.object(TaskExecutor, '_load_agent_runners'):
            executor = TaskExecutor()
            executor._agent_runners = {'partnerships': mock_runner}
            
            result = await executor.execute_task(task, state)
        
        assert result.success is False
        assert "Connection timeout" in result.error
    
    def test_build_task_prompt(self):
        """Test building a prompt from a task."""
        from src.graph.task_orchestrator import TaskExecutor
        from src.models.task_plan import Task
        
        task = Task(
            id="t1",
            agent="partnerships",
            action="add_partnership",
            parameters={
                "company": "Google",
                "contact_email": "john@google.com",
                "status": "Confirmed",
            },
            description="Add Google as a confirmed sponsor",
        )
        
        with patch.object(TaskExecutor, '_load_agent_runners'):
            executor = TaskExecutor()
            prompt = executor._build_task_prompt(task)
        
        assert "add_partnership" in prompt
        assert "Google" in prompt
        assert "john@google.com" in prompt
        assert "Confirmed" in prompt
        assert "Add Google as a confirmed sponsor" in prompt
    
    def test_build_task_prompt_empty_parameters(self):
        """Test building a prompt with no parameters."""
        from src.graph.task_orchestrator import TaskExecutor
        from src.models.task_plan import Task
        
        task = Task(
            id="t1",
            agent="events",
            action="get_summary",
            parameters={},
            description="Get event summary",
        )
        
        with patch.object(TaskExecutor, '_load_agent_runners'):
            executor = TaskExecutor()
            prompt = executor._build_task_prompt(task)
        
        assert "get_summary" in prompt
        assert "Get event summary" in prompt


# =============================================================================
# EVENT STREAMING TESTS
# =============================================================================

class TestTaskEventStreaming:
    """Tests for task event streaming."""
    
    @pytest.mark.asyncio
    async def test_orchestrate_with_events_generator(self):
        """Test the event generator function."""
        from src.graph.task_orchestrator import (
            orchestrate_with_events, 
            TaskExecutor, 
            TaskExecutionResult,
            TaskOrchestrator,
        )
        from src.models.task_plan import TaskPlan, Task
        from src.models.state import GraphState
        
        tasks = [
            Task(id="t1", agent="partnerships", action="log", parameters={}, description="Log"),
            Task(id="t2", agent="events", action="notify", parameters={}, description="Notify", depends_on=["t1"]),
        ]
        
        plan = TaskPlan(
            plan_id="test_plan",
            request_id="test_req",
            tasks=tasks,
            execution_strategy="mixed",
        )
        
        state = GraphState(request_id="test_req", user_message="test")
        
        # Mock the TaskExecutor's execute_task method
        with patch.object(TaskExecutor, '_load_agent_runners'):
            with patch.object(TaskExecutor, 'execute_task', new_callable=AsyncMock) as mock_exec:
                mock_exec.return_value = TaskExecutionResult(
                    task_id="",
                    success=True,
                    message="Success",
                )
                
                events = []
                async for event in orchestrate_with_events(plan, state):
                    events.append(event)
        
        # Should have events for plan start, tasks, plan complete
        event_types = [e.event_type for e in events]
        assert "plan_start" in event_types
        assert "plan_complete" in event_types
    
    @pytest.mark.asyncio
    async def test_task_event_to_dict(self):
        """Test converting task events to dictionary."""
        from src.graph.task_orchestrator import TaskEvent
        from src.models.task_plan import Task
        
        task = Task(id="t1", agent="partnerships", action="log", parameters={}, description="Log")
        
        event = TaskEvent(
            event_type="task_start",
            task_id="t1",
            task=task,
            data={"agent": "partnerships", "action": "log"},
        )
        
        event_dict = event.to_dict()
        
        assert event_dict["event_type"] == "task_start"
        assert event_dict["task_id"] == "t1"
        assert event_dict["task"]["agent"] == "partnerships"
        assert event_dict["data"]["action"] == "log"
        assert "timestamp" in event_dict
    
    @pytest.mark.asyncio
    async def test_events_emitted_in_order(self):
        """Test that events are emitted in the correct order."""
        from src.graph.task_orchestrator import TaskOrchestrator, TaskExecutor, TaskExecutionResult
        from src.models.task_plan import TaskPlan, Task
        from src.models.state import GraphState
        
        tasks = [
            Task(id="t1", agent="partnerships", action="log", parameters={}, description="Log"),
        ]
        
        plan = TaskPlan(
            plan_id="test_plan",
            request_id="test_req",
            tasks=tasks,
            execution_strategy="sequential",
        )
        
        events = []
        async def track_event(event):
            events.append(event.event_type)
        
        async def mock_execute(task, state):
            return TaskExecutionResult(task_id=task.id, success=True, message="Success")
        
        mock_executor = MagicMock(spec=TaskExecutor)
        mock_executor.execute_task = mock_execute
        
        orchestrator = TaskOrchestrator(mock_executor, track_event)
        state = GraphState(request_id="test_req", user_message="test")
        
        await orchestrator.execute_plan(plan, state)
        
        # Events should be in order: plan_start -> task_start -> task_complete -> plan_complete
        assert events[0] == "plan_start"
        assert events[1] == "task_start"
        assert events[2] == "task_complete"
        assert events[-1] == "plan_complete"
    
    @pytest.mark.asyncio  
    async def test_failed_task_emits_failure_event(self):
        """Test that failed tasks emit the correct event."""
        from src.graph.task_orchestrator import TaskOrchestrator, TaskExecutor, TaskExecutionResult
        from src.models.task_plan import TaskPlan, Task
        from src.models.state import GraphState
        
        tasks = [
            Task(id="t1", agent="partnerships", action="log", parameters={}, description="Log"),
        ]
        
        plan = TaskPlan(
            plan_id="test_plan",
            request_id="test_req",
            tasks=tasks,
            execution_strategy="sequential",
        )
        
        events = []
        async def track_event(event):
            events.append(event)
        
        async def mock_execute(task, state):
            return TaskExecutionResult(
                task_id=task.id, 
                success=False, 
                message="Failed",
                error="Database connection error"
            )
        
        mock_executor = MagicMock(spec=TaskExecutor)
        mock_executor.execute_task = mock_execute
        
        orchestrator = TaskOrchestrator(mock_executor, track_event)
        state = GraphState(request_id="test_req", user_message="test")
        
        await orchestrator.execute_plan(plan, state)
        
        # Should have a task_failed event
        failed_events = [e for e in events if e.event_type == "task_failed"]
        assert len(failed_events) == 1
        assert failed_events[0].data.get("error") == "Database connection error"


# =============================================================================
# EDGE CASE TESTS
# =============================================================================

class TestOrchestratorEdgeCases:
    """Tests for edge cases and error handling."""
    
    @pytest.mark.asyncio
    async def test_empty_plan(self):
        """Test executing an empty plan."""
        from src.graph.task_orchestrator import TaskOrchestrator, TaskExecutor
        from src.models.task_plan import TaskPlan
        from src.models.state import GraphState
        
        plan = TaskPlan(
            plan_id="empty_plan",
            request_id="test_req",
            tasks=[],
            execution_strategy="mixed",
        )
        
        mock_executor = MagicMock(spec=TaskExecutor)
        orchestrator = TaskOrchestrator(mock_executor)
        state = GraphState(request_id="test_req", user_message="test")
        
        results = await orchestrator.execute_plan(plan, state)
        
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_all_tasks_fail(self):
        """Test when all tasks fail."""
        from src.graph.task_orchestrator import TaskOrchestrator, TaskExecutor, TaskExecutionResult
        from src.models.task_plan import TaskPlan, Task
        from src.models.state import GraphState
        
        tasks = [
            Task(id="t1", agent="partnerships", action="log", parameters={}, description="Task 1"),
            Task(id="t2", agent="events", action="notify", parameters={}, description="Task 2"),
        ]
        
        plan = TaskPlan(
            plan_id="test_plan",
            request_id="test_req",
            tasks=tasks,
            execution_strategy="parallel",
        )
        
        async def mock_execute(task, state):
            return TaskExecutionResult(
                task_id=task.id,
                success=False,
                message="Failed",
                error="Service unavailable",
            )
        
        mock_executor = MagicMock(spec=TaskExecutor)
        mock_executor.execute_task = mock_execute
        
        orchestrator = TaskOrchestrator(mock_executor)
        state = GraphState(request_id="test_req", user_message="test")
        
        results = await orchestrator.execute_plan(plan, state)
        
        assert len(orchestrator.failed_task_ids) == 2
        assert len(orchestrator.completed_task_ids) == 0
    
    @pytest.mark.asyncio
    async def test_diamond_dependency_pattern(self):
        """Test diamond dependency: t1 -> [t2, t3] -> t4."""
        from src.graph.task_orchestrator import TaskOrchestrator, TaskExecutor, TaskExecutionResult
        from src.models.task_plan import TaskPlan, Task
        from src.models.state import GraphState
        
        #     t1
        #    /  \
        #   t2  t3
        #    \  /
        #     t4
        tasks = [
            Task(id="t1", agent="partnerships", action="a1", parameters={}, description="Task 1"),
            Task(id="t2", agent="events", action="a2", parameters={}, description="Task 2", depends_on=["t1"]),
            Task(id="t3", agent="finance", action="a3", parameters={}, description="Task 3", depends_on=["t1"]),
            Task(id="t4", agent="marketing", action="a4", parameters={}, description="Task 4", depends_on=["t2", "t3"]),
        ]
        
        plan = TaskPlan(
            plan_id="test_plan",
            request_id="test_req",
            tasks=tasks,
            execution_strategy="mixed",
        )
        
        execution_order = []
        
        async def mock_execute(task, state):
            execution_order.append(task.id)
            return TaskExecutionResult(task_id=task.id, success=True, message="Success")
        
        mock_executor = MagicMock(spec=TaskExecutor)
        mock_executor.execute_task = mock_execute
        
        orchestrator = TaskOrchestrator(mock_executor)
        state = GraphState(request_id="test_req", user_message="test")
        
        await orchestrator.execute_plan(plan, state)
        
        # t1 must come first
        assert execution_order[0] == "t1"
        # t4 must come last
        assert execution_order[-1] == "t4"
        # t2 and t3 must come before t4
        assert execution_order.index("t2") < execution_order.index("t4")
        assert execution_order.index("t3") < execution_order.index("t4")
    
    @pytest.mark.asyncio
    async def test_diamond_with_failure(self):
        """Test diamond pattern where one branch fails."""
        from src.graph.task_orchestrator import TaskOrchestrator, TaskExecutor, TaskExecutionResult
        from src.models.task_plan import TaskPlan, Task
        from src.models.state import GraphState
        
        #     t1
        #    /  \
        #   t2  t3 (fails)
        #    \  /
        #     t4 (should be skipped)
        tasks = [
            Task(id="t1", agent="partnerships", action="a1", parameters={}, description="Task 1"),
            Task(id="t2", agent="events", action="a2", parameters={}, description="Task 2", depends_on=["t1"]),
            Task(id="t3", agent="finance", action="a3", parameters={}, description="Task 3", depends_on=["t1"]),
            Task(id="t4", agent="marketing", action="a4", parameters={}, description="Task 4", depends_on=["t2", "t3"]),
        ]
        
        plan = TaskPlan(
            plan_id="test_plan",
            request_id="test_req",
            tasks=tasks,
            execution_strategy="mixed",
        )
        
        async def mock_execute(task, state):
            if task.id == "t3":
                return TaskExecutionResult(task_id=task.id, success=False, message="Failed", error="Error")
            return TaskExecutionResult(task_id=task.id, success=True, message="Success")
        
        mock_executor = MagicMock(spec=TaskExecutor)
        mock_executor.execute_task = mock_execute
        
        orchestrator = TaskOrchestrator(mock_executor)
        state = GraphState(request_id="test_req", user_message="test")
        
        results = await orchestrator.execute_plan(plan, state)
        
        # t1 and t2 should complete
        assert "t1" in orchestrator.completed_task_ids
        assert "t2" in orchestrator.completed_task_ids
        # t3 should fail
        assert "t3" in orchestrator.failed_task_ids
        # t4 should be skipped (one of its dependencies failed)
        assert results["t4"].success is False
        assert "Skipped" in results["t4"].message
    
    @pytest.mark.asyncio
    async def test_task_with_exception(self):
        """Test handling when executor raises an exception."""
        from src.graph.task_orchestrator import TaskOrchestrator, TaskExecutor, TaskExecutionResult
        from src.models.task_plan import TaskPlan, Task
        from src.models.state import GraphState
        
        tasks = [
            Task(id="t1", agent="partnerships", action="log", parameters={}, description="Task 1"),
        ]
        
        plan = TaskPlan(
            plan_id="test_plan",
            request_id="test_req",
            tasks=tasks,
            execution_strategy="sequential",
        )
        
        async def mock_execute(task, state):
            raise RuntimeError("Unexpected error")
        
        mock_executor = MagicMock(spec=TaskExecutor)
        mock_executor.execute_task = mock_execute
        
        events = []
        async def track_event(event):
            events.append(event)
        
        orchestrator = TaskOrchestrator(mock_executor, track_event)
        state = GraphState(request_id="test_req", user_message="test")
        
        results = await orchestrator.execute_plan(plan, state)
        
        # Task should be marked as failed
        assert "t1" in orchestrator.failed_task_ids
        assert "Unexpected error" in results["t1"].error
        
        # Should have emitted error event
        error_events = [e for e in events if e.event_type == "task_error"]
        assert len(error_events) == 1
    
    @pytest.mark.asyncio
    async def test_multiple_approval_tasks(self):
        """Test plan with multiple approval-required tasks."""
        from src.graph.task_orchestrator import TaskOrchestrator, TaskExecutor, TaskExecutionResult
        from src.models.task_plan import TaskPlan, Task
        from src.models.state import GraphState
        
        tasks = [
            Task(id="t1", agent="finance", action="invoice1", parameters={}, description="Invoice 1", requires_approval=True),
            Task(id="t2", agent="finance", action="invoice2", parameters={}, description="Invoice 2", requires_approval=True),
            Task(id="t3", agent="finance", action="mou", parameters={}, description="MOU", requires_approval=True),
        ]
        
        plan = TaskPlan(
            plan_id="test_plan",
            request_id="test_req",
            tasks=tasks,
            execution_strategy="parallel",
        )
        
        events = []
        async def track_event(event):
            events.append(event)
        
        mock_executor = MagicMock(spec=TaskExecutor)
        
        orchestrator = TaskOrchestrator(mock_executor, track_event)
        state = GraphState(request_id="test_req", user_message="test")
        
        results = await orchestrator.execute_plan(plan, state)
        
        # All should complete with approval required
        assert all(r.requires_approval for r in results.values())
        
        # Should have 3 approval events
        approval_events = [e for e in events if e.event_type == "task_approval_required"]
        assert len(approval_events) == 3


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestOrchestratorIntegration:
    """Integration tests for the orchestrator with real components."""
    
    @pytest.mark.asyncio
    async def test_full_workflow_simulation(self):
        """Simulate a full workflow execution."""
        from src.graph.task_orchestrator import TaskOrchestrator, TaskExecutor, TaskExecutionResult
        from src.models.task_plan import TaskPlan, Task, ExtractedEntity
        from src.models.state import GraphState
        
        # Simulate the Google sponsorship workflow
        tasks = [
            Task(
                id="task_1",
                agent="partnerships",
                action="add_partnership",
                parameters={
                    "sheet_name": "Boothing Companies",
                    "company": "Google",
                    "contact_name": "John Grey",
                    "status": "Confirmed",
                },
                description="Log Google sponsorship",
            ),
            Task(
                id="task_2",
                agent="events",
                action="send_team_message",
                parameters={
                    "channel": "#partnerships",
                    "message": "New sponsor: Google confirmed",
                },
                description="Notify partnerships channel",
                depends_on=["task_1"],
            ),
            Task(
                id="task_3",
                agent="events",
                action="send_team_message",
                parameters={
                    "channel": "#marketing",
                    "message": "Request assets from Google",
                },
                description="Notify marketing channel",
                depends_on=["task_1"],
            ),
            Task(
                id="task_4",
                agent="finance",
                action="draft_mou",
                parameters={"company": "Google", "amount": 1500},
                description="Draft MOU for Google",
                depends_on=["task_1"],
                requires_approval=True,
            ),
        ]
        
        entities = [
            ExtractedEntity(entity_type="company", value="Google", confidence=1.0),
            ExtractedEntity(entity_type="contact_name", value="John Grey", confidence=1.0),
            ExtractedEntity(entity_type="amount", value=1500, confidence=0.9),
        ]
        
        plan = TaskPlan(
            plan_id="sponsor_workflow",
            request_id="req_123",
            request_type="workflow",
            tasks=tasks,
            extracted_entities=entities,
            execution_strategy="mixed",
            target_agents=["partnerships", "events", "finance"],
        )
        
        # Track all events
        all_events = []
        async def track_event(event):
            all_events.append(event)
        
        # Mock executor that succeeds
        async def mock_execute(task, state):
            return TaskExecutionResult(
                task_id=task.id,
                success=True,
                message=f"Executed {task.action}",
                data={"task_id": task.id},
            )
        
        mock_executor = MagicMock(spec=TaskExecutor)
        mock_executor.execute_task = mock_execute
        
        orchestrator = TaskOrchestrator(mock_executor, track_event)
        state = GraphState(request_id="req_123", user_message="Add Google as sponsor")
        
        results = await orchestrator.execute_plan(plan, state)
        
        # Verify execution
        assert len(results) == 4
        
        # task_1 should complete first
        assert "task_1" in orchestrator.completed_task_ids
        
        # task_2, task_3, task_4 should all complete (task_4 with approval flag)
        assert "task_2" in orchestrator.completed_task_ids
        assert "task_3" in orchestrator.completed_task_ids
        assert "task_4" in orchestrator.completed_task_ids
        
        # task_4 should have approval required
        assert results["task_4"].requires_approval is True
        
        # Check event flow
        event_types = [e.event_type for e in all_events]
        assert event_types[0] == "plan_start"
        assert event_types[-1] == "plan_complete"
        
        # Should have approval event for task_4
        approval_events = [e for e in all_events if e.event_type == "task_approval_required"]
        assert len(approval_events) == 1


# =============================================================================
# STREAMING API INTEGRATION TESTS
# =============================================================================

class TestStreamingIntegration:
    """Tests for streaming API integration with task orchestration."""
    
    @pytest.mark.asyncio
    async def test_create_stream_event_task_plan(self):
        """Test creating stream events for task plan."""
        from src.api.streaming import create_stream_event
        import json
        
        event_str = create_stream_event(
            "task_plan",
            {
                "plan_id": "plan_123",
                "total_tasks": 3,
                "execution_strategy": "mixed",
            },
        )
        
        event_data = json.loads(event_str)
        
        assert event_data["event_type"] == "task_plan"
        assert event_data["data"]["plan_id"] == "plan_123"
        assert event_data["data"]["total_tasks"] == 3
    
    @pytest.mark.asyncio
    async def test_create_stream_event_task_complete(self):
        """Test creating stream events for task completion."""
        from src.api.streaming import create_stream_event
        import json
        
        event_str = create_stream_event(
            "task_complete",
            {
                "task_id": "t1",
                "status": "success",
                "message": "Added Google to sponsors",
                "execution_time": 0.5,
            },
            agent_name="partnerships",
        )
        
        event_data = json.loads(event_str)
        
        assert event_data["event_type"] == "task_complete"
        assert event_data["agent_name"] == "partnerships"
        assert event_data["data"]["task_id"] == "t1"


# =============================================================================
# PERFORMANCE AND CONCURRENCY TESTS
# =============================================================================

class TestConcurrency:
    """Tests for concurrent execution behavior."""
    
    @pytest.mark.asyncio
    async def test_parallel_tasks_run_concurrently(self):
        """Verify that independent tasks actually run in parallel."""
        from src.graph.task_orchestrator import TaskOrchestrator, TaskExecutor, TaskExecutionResult
        from src.models.task_plan import TaskPlan, Task
        from src.models.state import GraphState
        import time
        
        # Create 3 independent tasks
        tasks = [
            Task(id="t1", agent="partnerships", action="a1", parameters={}, description="Task 1"),
            Task(id="t2", agent="events", action="a2", parameters={}, description="Task 2"),
            Task(id="t3", agent="finance", action="a3", parameters={}, description="Task 3"),
        ]
        
        plan = TaskPlan(
            plan_id="test_plan",
            request_id="test_req",
            tasks=tasks,
            execution_strategy="mixed",  # Should parallelize since no dependencies
        )
        
        # Each task takes 0.1 seconds
        async def mock_execute(task, state):
            await asyncio.sleep(0.1)
            return TaskExecutionResult(task_id=task.id, success=True, message="Success")
        
        mock_executor = MagicMock(spec=TaskExecutor)
        mock_executor.execute_task = mock_execute
        
        orchestrator = TaskOrchestrator(mock_executor)
        state = GraphState(request_id="test_req", user_message="test")
        
        start = time.time()
        await orchestrator.execute_plan(plan, state)
        elapsed = time.time() - start
        
        # If parallel: ~0.1s, if sequential: ~0.3s
        # Allow some overhead but should be significantly less than sequential
        assert elapsed < 0.25, f"Tasks should run in parallel, took {elapsed}s"
    
    @pytest.mark.asyncio
    async def test_dependent_tasks_run_sequentially(self):
        """Verify that dependent tasks wait for their dependencies."""
        from src.graph.task_orchestrator import TaskOrchestrator, TaskExecutor, TaskExecutionResult
        from src.models.task_plan import TaskPlan, Task
        from src.models.state import GraphState
        import time
        
        # Create chain: t1 -> t2 -> t3
        tasks = [
            Task(id="t1", agent="partnerships", action="a1", parameters={}, description="Task 1"),
            Task(id="t2", agent="events", action="a2", parameters={}, description="Task 2", depends_on=["t1"]),
            Task(id="t3", agent="finance", action="a3", parameters={}, description="Task 3", depends_on=["t2"]),
        ]
        
        plan = TaskPlan(
            plan_id="test_plan",
            request_id="test_req",
            tasks=tasks,
            execution_strategy="mixed",
        )
        
        timestamps = {}
        
        async def mock_execute(task, state):
            timestamps[f"{task.id}_start"] = time.time()
            await asyncio.sleep(0.05)
            timestamps[f"{task.id}_end"] = time.time()
            return TaskExecutionResult(task_id=task.id, success=True, message="Success")
        
        mock_executor = MagicMock(spec=TaskExecutor)
        mock_executor.execute_task = mock_execute
        
        orchestrator = TaskOrchestrator(mock_executor)
        state = GraphState(request_id="test_req", user_message="test")
        
        await orchestrator.execute_plan(plan, state)
        
        # t2 should start after t1 ends
        assert timestamps["t2_start"] >= timestamps["t1_end"]
        # t3 should start after t2 ends
        assert timestamps["t3_start"] >= timestamps["t2_end"]


# =============================================================================
# TASK EXECUTION RESULT TESTS
# =============================================================================

class TestTaskExecutionResult:
    """Tests for TaskExecutionResult class."""
    
    def test_result_creation(self):
        """Test creating a task execution result."""
        from src.graph.task_orchestrator import TaskExecutionResult
        
        result = TaskExecutionResult(
            task_id="t1",
            success=True,
            message="Task completed successfully",
            data={"company": "Google"},
            execution_time=0.5,
        )
        
        assert result.task_id == "t1"
        assert result.success is True
        assert result.message == "Task completed successfully"
        assert result.data["company"] == "Google"
        assert result.execution_time == 0.5
    
    def test_result_with_error(self):
        """Test creating a failed task result."""
        from src.graph.task_orchestrator import TaskExecutionResult
        
        result = TaskExecutionResult(
            task_id="t1",
            success=False,
            message="Task failed",
            error="Connection timeout",
        )
        
        assert result.success is False
        assert result.error == "Connection timeout"
    
    def test_result_with_approval(self):
        """Test creating an approval-required result."""
        from src.graph.task_orchestrator import TaskExecutionResult
        
        result = TaskExecutionResult(
            task_id="t1",
            success=True,
            message="Awaiting approval",
            requires_approval=True,
            approval_data={
                "action": "generate_invoice",
                "amount": 1500,
            },
        )
        
        assert result.requires_approval is True
        assert result.approval_data["action"] == "generate_invoice"


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
