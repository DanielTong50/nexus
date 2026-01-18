"""
Finance Agent for Nexus.

Handles MOUs, invoices, and budget management.
Uses LLM to intelligently select and execute tools.
"""

import logging
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from config.settings import settings
from src.agents.base import BaseAgent, AgentResult

logger = logging.getLogger(__name__)

FINANCE_SYSTEM_PROMPT = """You are the Finance Agent for Nexus, an AI-powered event production platform.

Your responsibilities include:
- Checking and reporting budget status
- Drafting MOUs for sponsors (requires approval)
- Generating invoices (requires approval)
- Updating budget sheets
- Providing sponsorship financial summaries

When responding:
1. Be precise with numbers and financial data
2. Always flag MOUs and invoices for approval
3. Provide clear breakdowns of financial information
4. Warn about budget concerns proactively

Be accurate, professional, and transparent with all financial matters."""


class FinanceAgent(BaseAgent):
    """Agent responsible for financial operations."""

    def __init__(self):
        super().__init__(agent_name="finance")
        self._register_tools()
        self.llm = None

    def _get_llm(self):
        if self.llm is None:
            self.llm = ChatGoogleGenerativeAI(
                model=settings.agent_model,
                google_api_key=settings.google_api_key,
                temperature=0.2,  # Lower temperature for accuracy
            )
        return self.llm

    def _register_tools(self):
        from src.tools.finance import (
            check_budget_status,
            update_budget_sheet,
            draft_mou,
            generate_invoice,
            get_sponsorship_financials,
        )

        self.tools = [
            check_budget_status,
            update_budget_sheet,
            draft_mou,
            generate_invoice,
            get_sponsorship_financials,
        ]

    async def execute(self, prompt: str, context: dict[str, Any]) -> AgentResult:
        tool_calls = []
        pending_actions = []

        try:
            llm = self._get_llm()
            llm_with_tools = llm.bind_tools(self.tools)

            messages = [
                SystemMessage(content=FINANCE_SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await llm_with_tools.ainvoke(messages)

            if response.tool_calls:
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    logger.info(f"Finance agent calling tool: {tool_name}")

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
            logger.error(f"Finance agent error: {e}")
            return self._create_error_result(str(e))


finance_agent = FinanceAgent()
