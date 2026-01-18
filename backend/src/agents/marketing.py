"""
Marketing Agent for Nexus.

Handles content creation, social media scheduling, and campaign management.
Uses LLM to intelligently select and execute tools.
"""

import logging
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from config.settings import settings
from src.agents.base import BaseAgent, AgentResult

logger = logging.getLogger(__name__)

MARKETING_SYSTEM_PROMPT = """You are the Marketing Agent for Nexus, an AI-powered event production platform.

Your responsibilities include:
- Creating content timelines for events
- Drafting social media posts for Instagram, LinkedIn, Twitter
- Checking design asset status in Figma
- Scheduling social media posts (requires approval)
- Generating marketing campaign ideas
- Coordinating sponsor visibility in content

When responding:
1. Understand the marketing goal
2. Use appropriate tools to create or schedule content
3. Present drafts for review before scheduling
4. Flag posts that need approval

Be creative, on-brand, and engaging. Use emojis sparingly and professionally."""


class MarketingAgent(BaseAgent):
    """Agent responsible for marketing and content."""

    def __init__(self):
        super().__init__(agent_name="marketing")
        self._register_tools()
        self.llm = None

    def _get_llm(self):
        if self.llm is None:
            self.llm = ChatGoogleGenerativeAI(
                model=settings.agent_model,
                google_api_key=settings.google_api_key,
                temperature=0.7,  # More creative for marketing
            )
        return self.llm

    def _register_tools(self):
        from src.tools.figma import check_figma_asset
        from src.tools.social import (
            draft_social_post,
            create_content_timeline,
            schedule_instagram_post,
            schedule_linkedin_post,
            generate_campaign_ideas,
            update_sponsor_in_content,
        )

        self.tools = [
            draft_social_post,
            create_content_timeline,
            check_figma_asset,
            schedule_instagram_post,
            schedule_linkedin_post,
            generate_campaign_ideas,
            update_sponsor_in_content,
        ]

    async def execute(self, prompt: str, context: dict[str, Any]) -> AgentResult:
        tool_calls = []
        pending_actions = []

        try:
            llm = self._get_llm()
            llm_with_tools = llm.bind_tools(self.tools)

            messages = [
                SystemMessage(content=MARKETING_SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await llm_with_tools.ainvoke(messages)

            if response.tool_calls:
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    logger.info(f"Marketing agent calling tool: {tool_name}")

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
            logger.error(f"Marketing agent error: {e}")
            return self._create_error_result(str(e))


marketing_agent = MarketingAgent()
