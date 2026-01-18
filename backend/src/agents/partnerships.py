"""
Partnerships Agent for Nexus.

Handles sponsor, judge, mentor, and student mentor outreach and tracking.
Uses LLM to intelligently select and execute tools.
"""

import logging
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from config.settings import settings
from config.prompts import PARTNERSHIPS_SYSTEM_PROMPT
from src.agents.base import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class PartnershipsAgent(BaseAgent):
    """
    Agent responsible for partnership management.

    Uses Gemini to intelligently route requests to appropriate tools.
    """

    def __init__(self):
        super().__init__(agent_name="partnerships")
        self._register_tools()
        self.llm = None

    def _get_llm(self):
        """Get or create the LLM instance."""
        if self.llm is None:
            self.llm = ChatGoogleGenerativeAI(
                model=settings.agent_model,
                google_api_key=settings.google_api_key,
                temperature=0.3,
            )
        return self.llm

    def _register_tools(self):
        """Register tools available to this agent."""
        from src.tools.google_sheets import (
            search_partnership_sheet,
            log_partnership_status,
            get_partnership_summary,
            get_partnership_details,
            add_partnership,
        )
        from src.tools.calendly import prepare_calendly_link
        from src.tools.social import (
            draft_linkedin_outreach,
            draft_email_outreach,
        )

        self.tools = [
            search_partnership_sheet,
            log_partnership_status,
            get_partnership_summary,
            get_partnership_details,
            add_partnership,
            prepare_calendly_link,
            draft_linkedin_outreach,
            draft_email_outreach,
        ]

    async def execute(self, prompt: str, context: dict[str, Any]) -> AgentResult:
        """
        Execute partnership-related task using LLM.

        Args:
            prompt: The sub-prompt from the router
            context: Event context, user info, etc.

        Returns:
            AgentResult with execution details
        """
        tool_calls = []
        pending_actions = []

        try:
            llm = self._get_llm()

            # Bind tools to LLM
            llm_with_tools = llm.bind_tools(self.tools)

            # Create messages
            messages = [
                SystemMessage(content=PARTNERSHIPS_SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            # Get LLM response with potential tool calls
            response = await llm_with_tools.ainvoke(messages)

            # Process tool calls if any
            if response.tool_calls:
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    logger.info(f"Partnerships agent calling tool: {tool_name}")

                    # Find and execute the tool
                    tool_result = None
                    for tool in self.tools:
                        if tool.name == tool_name:
                            try:
                                tool_result = await tool.ainvoke(tool_args)
                            except Exception as e:
                                tool_result = f"Error: {str(e)}"
                            break

                    tool_calls.append({
                        "tool_name": tool_name,
                        "input": tool_args,
                        "output": tool_result,
                        "status": "success" if tool_result and "Error" not in str(tool_result) else "error",
                    })

                    # Check if action requires approval
                    if self.requires_approval(tool_name):
                        pending_actions.append({
                            "action": tool_name,
                            "args": tool_args,
                            "preview": tool_result,
                        })

                # Get final response incorporating tool results
                tool_results_text = "\n".join([
                    f"Tool: {tc['tool_name']}\nResult: {tc['output']}"
                    for tc in tool_calls
                ])

                messages.append(response)
                messages.append(HumanMessage(content=f"Tool results:\n{tool_results_text}\n\nPlease provide a summary response for the user."))

                final_response = await llm.ainvoke(messages)
                response_text = final_response.content
            else:
                # No tool calls, use direct response
                response_text = response.content

            return self._create_success_result(
                message=response_text,
                tool_calls=tool_calls,
                pending_actions=pending_actions if pending_actions else None
            )

        except Exception as e:
            logger.error(f"Partnerships agent error: {e}")
            return self._create_error_result(str(e))

# Create singleton instance
partnerships_agent = PartnershipsAgent()
