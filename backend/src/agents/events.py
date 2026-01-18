"""
Events Agent for Nexus.

Handles logistics, venue bookings, scheduling, and team coordination.
Uses LLM to intelligently select and execute tools.
"""

import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from config.settings import settings
from config.prompts import EVENTS_SYSTEM_PROMPT
from src.agents.base import BaseAgent, AgentResult
from src.services.llm_factory import get_llm_for_agent

logger = logging.getLogger(__name__)


class EventsAgent(BaseAgent):
    """Agent responsible for event logistics."""

    def __init__(self):
        super().__init__(agent_name="events")
        self._register_tools()
        self.llm = None

    def _get_llm(self):
        if self.llm is None:
            # Uses Vultr (Llama 3.3 70B) if API key is configured
            self.llm = get_llm_for_agent(self.agent_name, temperature=0.3)
        return self.llm

    def _register_tools(self):
        from src.tools.events import (
            get_logistics_summary,
            update_logistics_sheet,
            generate_event_schedule,
            send_team_reminder,
            create_room_booking_request,
            send_availability_poll,
            announce_to_slack,
        )

        self.tools = [
            get_logistics_summary,
            update_logistics_sheet,
            generate_event_schedule,
            send_team_reminder,
            create_room_booking_request,
            send_availability_poll,
            announce_to_slack,
        ]

    async def execute(self, prompt: str, context: dict[str, Any]) -> AgentResult:
        tool_calls = []
        pending_actions = []

        try:
            llm = self._get_llm()
            llm_with_tools = llm.bind_tools(self.tools)

            messages = [
                SystemMessage(content=EVENTS_SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await llm_with_tools.ainvoke(messages)

            if response.tool_calls:
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    logger.info(f"Events agent calling tool: {tool_name}")

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

                    if self.requires_approval(tool_name):
                        pending_actions.append({
                            "action": tool_name,
                            "args": tool_args,
                            "preview": tool_result,
                        })

                tool_results_text = "\n".join([
                    f"Tool: {tc['tool_name']}\nResult: {tc['output']}"
                    for tc in tool_calls
                ])

                messages.append(response)
                messages.append(HumanMessage(content=f"Tool results:\n{tool_results_text}\n\nProvide a summary for the user."))

                final_response = await llm.ainvoke(messages)
                response_text = final_response.content
            else:
                response_text = response.content

            return self._create_success_result(
                message=response_text,
                tool_calls=tool_calls,
                pending_actions=pending_actions if pending_actions else None
            )

        except Exception as e:
            logger.error(f"Events agent error: {e}")
            return self._create_error_result(str(e))


events_agent = EventsAgent()
