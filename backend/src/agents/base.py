"""
Base Agent class for all Nexus agents.

All agents inherit from BaseAgent and implement their specific
tool bindings and execution logic.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import BaseModel, Field

from config.tool_schemas import HITL_REQUIRED_ACTIONS, HITL_NOTIFY_ACTIONS


class AgentResult(BaseModel):
    """Structured result from agent execution."""
    agent_name: str = Field(..., description="Name of the agent that produced this result")
    success: bool = Field(..., description="Whether the execution was successful")
    message: str = Field(..., description="Human-readable result message")
    tool_calls: list[dict] = Field(default_factory=list, description="List of tool calls made")
    requires_approval: bool = Field(False, description="Whether this result needs HITL approval")
    pending_actions: list[dict] = Field(default_factory=list, description="Actions pending approval")
    error: Optional[str] = Field(None, description="Error message if execution failed")
    # Clarification support
    needs_clarification: bool = Field(False, description="Whether agent needs more info from user")
    clarification_questions: Optional[list[str]] = Field(
        None, description="Questions to ask user when clarification is needed"
    )
    clarification_context: Optional[dict] = Field(
        None, description="Context to preserve for follow-up when clarification is provided"
    )


class AgentError(BaseModel):
    """Structured error from agent execution."""
    agent_name: str = Field(..., description="Name of the agent that failed")
    message: str = Field(..., description="Error message")
    recoverable: bool = Field(True, description="Whether the error is recoverable via retry")


class BaseAgent(ABC):
    """
    Abstract base class for all Nexus agents.
    
    Each agent specializes in a domain (partnerships, marketing, etc.)
    and has access to specific tools for that domain.
    
    Attributes:
        agent_name: Unique identifier for this agent
        tools: List of LangChain tools available to this agent
    """
    
    def __init__(self, agent_name: str):
        """Initialize the agent.
        
        Args:
            agent_name: Unique identifier for this agent
        """
        self.agent_name = agent_name
        self.tools: list = []
    
    @abstractmethod
    async def execute(self, prompt: str, context: dict[str, Any]) -> AgentResult:
        """
        Execute the agent's task based on the prompt.
        
        Args:
            prompt: The sub-prompt assigned to this agent by the router
            context: Additional context including event info, user info, etc.
            
        Returns:
            AgentResult with execution details
        """
        pass
    
    def get_tools(self) -> list:
        """Return the list of tools available to this agent."""
        return self.tools
    
    def requires_approval(self, action: str) -> bool:
        """
        Check if an action requires human-in-the-loop approval.
        
        Args:
            action: The tool/action name to check
            
        Returns:
            True if the action requires approval before execution
        """
        return action in HITL_REQUIRED_ACTIONS
    
    def should_notify(self, action: str) -> bool:
        """
        Check if an action should notify the user (but not block).
        
        Args:
            action: The tool/action name to check
            
        Returns:
            True if the action should send a notification
        """
        return action in HITL_NOTIFY_ACTIONS
    
    async def validate_output(self, output: Any) -> bool:
        """
        Validate the output of a tool call.
        
        Override in subclasses for domain-specific validation.
        
        Args:
            output: The output to validate
            
        Returns:
            True if the output is valid
        """
        if output is None:
            return False
        if isinstance(output, str) and "error" in output.lower():
            return False
        return True
    
    def _create_success_result(
        self,
        message: str,
        tool_calls: list[dict],
        pending_actions: Optional[list[dict]] = None
    ) -> AgentResult:
        """Helper to create a successful result."""
        return AgentResult(
            agent_name=self.agent_name,
            success=True,
            message=message,
            tool_calls=tool_calls,
            requires_approval=bool(pending_actions),
            pending_actions=pending_actions or []
        )
    
    def _create_error_result(self, error: str) -> AgentResult:
        """Helper to create an error result."""
        return AgentResult(
            agent_name=self.agent_name,
            success=False,
            message=f"Agent {self.agent_name} encountered an error",
            error=error
        )

    def _create_clarification_result(
        self,
        questions: list[str],
        context: dict,
        message: Optional[str] = None,
    ) -> AgentResult:
        """
        Helper to create a result requesting user clarification.
        
        Args:
            questions: List of questions to ask the user
            context: Context to preserve for when user responds
            message: Optional message explaining what's needed
            
        Returns:
            AgentResult with needs_clarification=True
        """
        return AgentResult(
            agent_name=self.agent_name,
            success=True,  # Not a failure, just needs more info
            message=message or "I need some additional information to proceed.",
            needs_clarification=True,
            clarification_questions=questions,
            clarification_context=context,
        )
