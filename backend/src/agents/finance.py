"""
Finance Agent for Nexus.

Handles MOUs, invoices, and budget management.
"""

from typing import Any

from src.agents.base import BaseAgent, AgentResult


class FinanceAgent(BaseAgent):
    """
    Agent responsible for financial operations.
    
    Capabilities:
    - Draft MOUs for sponsors
    - Generate invoices
    - Update budget sheets
    - Check budget status
    - Summarize sponsorship financials
    
    Note: MOU drafts and invoice generation require HITL approval.
    """
    
    def __init__(self):
        super().__init__(agent_name="finance")
        self._register_tools()
    
    def _register_tools(self):
        """Register tools available to this agent."""
        from src.tools.google_sheets import (
            update_budget_sheet,
            check_budget_status,
            get_sponsorship_financials,
        )
        from src.tools.social import (
            draft_mou,
            generate_invoice,
        )
        
        self.tools = [
            draft_mou,
            generate_invoice,
            update_budget_sheet,
            check_budget_status,
            get_sponsorship_financials,
        ]
    
    async def execute(self, prompt: str, context: dict[str, Any]) -> AgentResult:
        """
        Execute finance-related task.
        
        Args:
            prompt: The sub-prompt from the router
            context: Event context, user info, etc.
            
        Returns:
            AgentResult with execution details
        """
        tool_calls = []
        pending_actions = []
        
        # Placeholder: Phase 2 implementation
        # Finance agent should always queue MOUs and invoices for approval
        
        return self._create_success_result(
            message=f"Finance agent processed: {prompt[:50]}...",
            tool_calls=tool_calls,
            pending_actions=pending_actions
        )
