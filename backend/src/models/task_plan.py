"""Task planning models for structured workflow decomposition.

These models represent the output of the enhanced classifier, which
decomposes complex user requests into ordered, dependency-aware tasks.

Example:
    User: "Log sponsor in compendium, notify partnerships, draft MOU"
    
    TaskPlan:
        - Task 1: log_partnership_status (no dependencies)
        - Task 2: send_team_message to #partnerships (depends on Task 1)
        - Task 3: draft_mou (depends on Task 1)
"""

from datetime import datetime
from typing import Literal, Optional, Any

from pydantic import BaseModel, Field


# Task execution status
TaskStatus = Literal["pending", "running", "completed", "failed", "skipped"]

# Request types for classification
RequestType = Literal["workflow", "question", "simple_task", "unknown"]

# Execution strategies
ExecutionStrategy = Literal["parallel", "sequential", "mixed"]


class ExtractedEntity(BaseModel):
    """Entity extracted from the user's message.
    
    Examples:
        - Company: "Google"
        - Contact: "John Grey"
        - Email: "john@gmail.com"
        - Amount: 1500.0
    """
    entity_type: str = Field(..., description="Type of entity (company, contact, email, amount, etc.)")
    value: Any = Field(..., description="Extracted value")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction confidence")


class Task(BaseModel):
    """Individual task in a workflow plan.
    
    Each task represents a specific action to be executed by an agent,
    with explicit dependencies on other tasks.
    """
    
    # Task identification
    id: str = Field(..., description="Unique task identifier (e.g., 'task_1')")
    
    # Routing
    agent: str = Field(..., description="Target agent (partnerships, marketing, finance, events, developers)")
    
    # Action specification
    action: str = Field(..., description="Tool/action name to execute (e.g., 'log_partnership_status')")
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters extracted from user message for this action"
    )
    
    # Human-readable description
    description: str = Field(..., description="What this task does in plain English")
    
    # Dependencies
    depends_on: list[str] = Field(
        default_factory=list,
        description="List of task IDs this task depends on"
    )
    
    # Execution state (updated during execution)
    status: TaskStatus = Field(default="pending", description="Current execution status")
    result: Optional[dict[str, Any]] = Field(default=None, description="Execution result")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    started_at: Optional[datetime] = Field(default=None, description="When execution started")
    completed_at: Optional[datetime] = Field(default=None, description="When execution completed")
    
    # Priority for ordering (1 = highest)
    priority: int = Field(default=1, ge=1, le=10, description="Execution priority")
    
    # Whether this task requires human approval before execution
    requires_approval: bool = Field(default=False, description="Whether HITL approval is needed")
    
    def is_ready(self, completed_tasks: set[str]) -> bool:
        """Check if this task is ready to execute.
        
        Args:
            completed_tasks: Set of task IDs that have completed
            
        Returns:
            True if all dependencies are satisfied
        """
        if not self.depends_on:
            return True
        return all(dep_id in completed_tasks for dep_id in self.depends_on)
    
    def mark_running(self) -> None:
        """Mark task as currently running."""
        self.status = "running"
        self.started_at = datetime.utcnow()
    
    def mark_completed(self, result: dict[str, Any]) -> None:
        """Mark task as successfully completed."""
        self.status = "completed"
        self.result = result
        self.completed_at = datetime.utcnow()
    
    def mark_failed(self, error: str) -> None:
        """Mark task as failed."""
        self.status = "failed"
        self.error = error
        self.completed_at = datetime.utcnow()
    
    def mark_skipped(self, reason: str = "Dependency failed") -> None:
        """Mark task as skipped due to dependency failure."""
        self.status = "skipped"
        self.error = reason
        self.completed_at = datetime.utcnow()


class TaskPlan(BaseModel):
    """Complete task plan from the classifier.
    
    Represents a decomposed workflow with tasks, dependencies,
    and execution strategy.
    """
    
    # Plan identification
    plan_id: str = Field(default="", description="Unique plan identifier")
    request_id: str = Field(default="", description="Associated request ID")
    
    # Classification metadata
    request_type: RequestType = Field(
        default="unknown",
        description="Type of request (workflow, question, simple_task)"
    )
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Classifier confidence in this plan"
    )
    reasoning: str = Field(
        default="",
        description="Classifier's reasoning for this decomposition"
    )
    
    # Tasks
    tasks: list[Task] = Field(
        default_factory=list,
        description="Ordered list of tasks to execute"
    )
    
    # Extracted entities from the original message
    extracted_entities: list[ExtractedEntity] = Field(
        default_factory=list,
        description="Entities extracted from user message"
    )
    
    # Execution configuration
    execution_strategy: ExecutionStrategy = Field(
        default="mixed",
        description="How to execute tasks (parallel, sequential, or mixed)"
    )
    
    # For backward compatibility - list of agents involved
    target_agents: list[str] = Field(
        default_factory=list,
        description="List of agents involved in this plan"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def get_ready_tasks(self, completed_tasks: set[str]) -> list[Task]:
        """Get all tasks that are ready to execute.
        
        Args:
            completed_tasks: Set of completed task IDs
            
        Returns:
            List of tasks ready for execution
        """
        return [
            task for task in self.tasks
            if task.status == "pending" 
            and task.id not in completed_tasks  # Exclude already completed
            and task.is_ready(completed_tasks)
        ]
    
    def get_pending_tasks(self) -> list[Task]:
        """Get all tasks still pending execution."""
        return [task for task in self.tasks if task.status == "pending"]
    
    def get_completed_tasks(self) -> list[Task]:
        """Get all completed tasks."""
        return [task for task in self.tasks if task.status == "completed"]
    
    def get_failed_tasks(self) -> list[Task]:
        """Get all failed tasks."""
        return [task for task in self.tasks if task.status == "failed"]
    
    def all_complete(self) -> bool:
        """Check if all tasks are complete (success, failed, or skipped)."""
        return all(
            task.status in ("completed", "failed", "skipped")
            for task in self.tasks
        )
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get a task by its ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def build_dependency_graph(self) -> dict[str, list[str]]:
        """Build a dependency graph for visualization.
        
        Returns:
            Dict mapping task_id to list of dependent task IDs
        """
        graph: dict[str, list[str]] = {task.id: [] for task in self.tasks}
        for task in self.tasks:
            for dep_id in task.depends_on:
                if dep_id in graph:
                    graph[dep_id].append(task.id)
        return graph
    
    def to_summary(self) -> dict:
        """Get a summary of the plan for logging/display."""
        return {
            "plan_id": self.plan_id,
            "request_type": self.request_type,
            "task_count": len(self.tasks),
            "agents": self.target_agents,
            "execution_strategy": self.execution_strategy,
            "tasks": [
                {
                    "id": t.id,
                    "agent": t.agent,
                    "action": t.action,
                    "description": t.description,
                    "depends_on": t.depends_on,
                    "status": t.status,
                }
                for t in self.tasks
            ],
        }


class QuestionPlan(BaseModel):
    """Plan for answering a question (simpler than workflow).
    
    Used when the request is a question rather than a workflow.
    """
    
    question: str = Field(..., description="The user's question")
    data_source: Literal["notion", "mongodb", "sheets", "unknown"] = Field(
        ...,
        description="Where to look for the answer"
    )
    query_type: Literal["search", "count", "lookup", "list"] = Field(
        default="search",
        description="Type of query to perform"
    )
    
    # Search parameters
    collection_or_sheet: str = Field(default="", description="Specific collection/sheet to query")
    search_terms: list[str] = Field(default_factory=list, description="Terms to search for")
    filters: dict[str, Any] = Field(default_factory=dict, description="Query filters")
    
    # Routing
    agent: str = Field(default="partnerships", description="Agent to handle this question")
    
    def to_task(self) -> Task:
        """Convert question plan to a single task."""
        action_map = {
            "notion": "search_notion",
            "mongodb": "query_event_data",
            "sheets": "search_partnership_sheet",
        }
        
        return Task(
            id="question_task",
            agent=self.agent,
            action=action_map.get(self.data_source, "search_partnership_sheet"),
            parameters={
                "query": self.question,
                "search_terms": self.search_terms,
                "filters": self.filters,
                "collection": self.collection_or_sheet,
            },
            description=f"Answer: {self.question}",
        )


# Helper function to create task plans
def create_task_plan(
    request_id: str,
    request_type: RequestType,
    tasks: list[dict],
    entities: list[dict] = None,
    execution_strategy: ExecutionStrategy = "mixed",
    reasoning: str = "",
) -> TaskPlan:
    """Create a TaskPlan from raw task dictionaries.
    
    Args:
        request_id: Associated request ID
        request_type: Type of request
        tasks: List of task dictionaries
        entities: List of extracted entity dictionaries
        execution_strategy: How to execute tasks
        reasoning: Classifier reasoning
        
    Returns:
        TaskPlan instance
    """
    task_objects = [Task(**t) for t in tasks]
    entity_objects = [ExtractedEntity(**e) for e in (entities or [])]
    
    # Extract unique agents
    target_agents = list(set(t.agent for t in task_objects))
    
    return TaskPlan(
        plan_id=f"plan_{request_id}",
        request_id=request_id,
        request_type=request_type,
        tasks=task_objects,
        extracted_entities=entity_objects,
        execution_strategy=execution_strategy,
        target_agents=target_agents,
        reasoning=reasoning,
    )
