"""
Developers Agent for Nexus.

Handles GitHub issues, PRs, and repository tracking.
Uses LLM to intelligently select and execute tools.
"""

import logging
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from config.settings import settings
from config.prompts import DEVELOPERS_SYSTEM_PROMPT
from src.agents.base import BaseAgent, AgentResult

logger = logging.getLogger(__name__)


class DevelopersAgent(BaseAgent):
    """Agent responsible for developer platform operations."""

    def __init__(self):
        super().__init__(agent_name="developers")
        self._register_tools()
        self.llm = None

    def _get_llm(self):
        if self.llm is None:
            self.llm = ChatGoogleGenerativeAI(
                model=settings.agent_model,
                google_api_key=settings.google_api_key,
                temperature=0.3,
            )
        return self.llm

    def _register_tools(self):
        from src.tools.github import (
            create_github_issue,
            check_pr_status,
            get_repo_updates,
            assign_issue,
        )

        self.tools = [
            create_github_issue,
            check_pr_status,
            get_repo_updates,
            assign_issue,
        ]

    async def execute(self, prompt: str, context: dict[str, Any]) -> AgentResult:
        tool_calls = []
        pending_actions = []

        try:
            llm = self._get_llm()
            llm_with_tools = llm.bind_tools(self.tools)

            messages = [
                SystemMessage(content=DEVELOPERS_SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await llm_with_tools.ainvoke(messages)

            if response.tool_calls:
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    logger.info(f"Developers agent calling tool: {tool_name}")

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
            logger.error(f"Developers agent error: {e}")
            return self._create_error_result(str(e))


developers_agent = DevelopersAgent()
