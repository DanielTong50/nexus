"""MCP Client Manager for external service integration.

Manages MCP server subprocesses using stdio transport for communication
with external services like Google Sheets, Slack, GitHub, etc.
"""

import asyncio
import json
import logging
import sys
from contextlib import asynccontextmanager
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from config.settings import settings


logger = logging.getLogger(__name__)


class MCPClientManager:
    """Manages MCP client sessions for external service integration.
    
    Uses stdio transport to spawn MCP servers as subprocesses and
    communicate with them for tool execution.
    """
    
    def __init__(self) -> None:
        self._sessions: dict[str, ClientSession] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._initialized = False
    
    async def start(self) -> None:
        """Initialize MCP client manager. Called on FastAPI startup."""
        if not settings.mcp_enabled:
            logger.info("MCP is disabled, skipping initialization")
            return
        
        logger.info("MCP Client Manager starting...")
        self._initialized = True
        logger.info("MCP Client Manager ready")
    
    async def stop(self) -> None:
        """Shutdown all MCP sessions. Called on FastAPI shutdown."""
        logger.info("MCP Client Manager shutting down...")
        
        for name, session in self._sessions.items():
            try:
                await session.__aexit__(None, None, None)
                logger.info(f"Closed MCP session: {name}")
            except Exception as e:
                logger.error(f"Error closing MCP session {name}: {e}")
        
        self._sessions.clear()
        self._locks.clear()
        self._initialized = False
        logger.info("MCP Client Manager stopped")
    
    @asynccontextmanager
    async def get_google_sheets_session(self):
        """Get or create a Google Sheets MCP session.
        
        Uses our custom Python-based MCP server that connects to
        Google Sheets API using service account credentials.
        
        Yields:
            ClientSession: Active MCP session for Google Sheets operations.
        """
        if not settings.mcp_enabled:
            raise RuntimeError("MCP is disabled")
        
        # Get the Python executable from the current environment
        python_executable = sys.executable
        
        # Our custom Python MCP server
        server_params = StdioServerParameters(
            command=python_executable,
            args=["-m", "src.mcp_servers.google_sheets_server"],
            env={
                "GOOGLE_SERVICE_ACCOUNT_JSON": settings.google_service_account_json,
                "GOOGLE_SHEETS_SPREADSHEET_ID": settings.google_sheets_spreadsheet_id,
            },
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session
    
    async def call_google_sheets_tool(
        self, 
        tool_name: str, 
        arguments: dict[str, Any]
    ) -> Any:
        """Call a Google Sheets MCP tool.
        
        Args:
            tool_name: Name of the MCP tool to call (e.g., "read_range", "append_row")
            arguments: Tool arguments as a dictionary
            
        Returns:
            Tool execution result (parsed from JSON)
        """
        try:
            async with self.get_google_sheets_session() as session:
                result = await session.call_tool(tool_name, arguments)
                
                # Parse the result content
                if result.content and len(result.content) > 0:
                    text_content = result.content[0]
                    if hasattr(text_content, 'text'):
                        try:
                            return json.loads(text_content.text)
                        except json.JSONDecodeError:
                            return text_content.text
                return result.content
        except Exception as e:
            logger.error(f"MCP tool call failed: {tool_name} - {e}")
            raise
    
    @asynccontextmanager
    async def get_slack_session(self, user_id: str | None = None):
        """Get or create a Slack MCP session.
        
        Uses our custom Python-based MCP server that connects to
        Slack API. Supports per-user OAuth tokens or fallback to bot token.
        
        Args:
            user_id: Optional user ID to fetch OAuth token for
        
        Yields:
            ClientSession: Active MCP session for Slack operations.
        """
        if not settings.mcp_enabled:
            raise RuntimeError("MCP is disabled")
        
        # Get token from TokenService if user_id provided
        token = None
        if user_id:
            from src.services.token_service import token_service
            token = await token_service.get_token(user_id, "slack")
            if token:
                logger.debug(f"Using OAuth token for user {user_id} (Slack)")
        
        # Fall back to environment variable
        if not token:
            token = settings.slack_bot_token
            logger.debug("Using fallback bot token for Slack")
        
        if not token:
            raise RuntimeError("No Slack token available - connect Slack or set SLACK_BOT_TOKEN")
        
        # Import here to avoid circular imports
        from src.tools.slack import get_allowed_channels_str
        
        # Get the Python executable from the current environment
        python_executable = sys.executable
        
        # Our custom Python MCP server
        server_params = StdioServerParameters(
            command=python_executable,
            args=["-m", "src.mcp_servers.slack_server"],
            env={
                "SLACK_BOT_TOKEN": token,
                "SLACK_ALLOWED_CHANNELS": get_allowed_channels_str(),
            },
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session
    
    async def call_slack_tool(
        self, 
        tool_name: str, 
        arguments: dict[str, Any],
        user_id: str | None = None
    ) -> Any:
        """Call a Slack MCP tool.
        
        Args:
            tool_name: Name of the MCP tool to call (e.g., "post_message", "list_channels")
            arguments: Tool arguments as a dictionary
            user_id: Optional user ID for per-user OAuth token
            
        Returns:
            Tool execution result (parsed from JSON)
        """
        try:
            async with self.get_slack_session(user_id=user_id) as session:
                result = await session.call_tool(tool_name, arguments)
                
                # Parse the result content
                if result.content and len(result.content) > 0:
                    text_content = result.content[0]
                    if hasattr(text_content, 'text'):
                        try:
                            return json.loads(text_content.text)
                        except json.JSONDecodeError:
                            return text_content.text
                return result.content
        except Exception as e:
            logger.error(f"MCP Slack tool call failed: {tool_name} - {e}")
            raise
    
    # =========================================================================
    # GitHub MCP
    # =========================================================================
    
    @asynccontextmanager
    async def get_github_session(self, user_id: str | None = None):
        """Get or create a GitHub MCP session.
        
        Args:
            user_id: Optional user ID to fetch OAuth token for
        """
        if not settings.mcp_enabled:
            raise RuntimeError("MCP is disabled")
        
        # Get token from TokenService if user_id provided
        token = None
        if user_id:
            from src.services.token_service import token_service
            token = await token_service.get_token(user_id, "github")
            if token:
                logger.debug(f"Using OAuth token for user {user_id} (GitHub)")
        
        # Fall back to environment variable
        if not token:
            token = settings.github_token
            logger.debug("Using fallback token for GitHub")
        
        if not token:
            raise RuntimeError("No GitHub token available - connect GitHub or set GITHUB_TOKEN")
        
        python_executable = sys.executable
        
        server_params = StdioServerParameters(
            command=python_executable,
            args=["-m", "src.mcp_servers.github_server"],
            env={
                "GITHUB_TOKEN": token,
                "GITHUB_DEFAULT_OWNER": getattr(settings, 'github_default_owner', ''),
            },
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session
    
    async def call_github_tool(
        self, 
        tool_name: str, 
        arguments: dict[str, Any],
        user_id: str | None = None
    ) -> Any:
        """Call a GitHub MCP tool.
        
        Args:
            tool_name: Name of the MCP tool to call
            arguments: Tool arguments as a dictionary
            user_id: Optional user ID for per-user OAuth token
        """
        try:
            async with self.get_github_session(user_id=user_id) as session:
                result = await session.call_tool(tool_name, arguments)
                
                if result.content and len(result.content) > 0:
                    text_content = result.content[0]
                    if hasattr(text_content, 'text'):
                        try:
                            return json.loads(text_content.text)
                        except json.JSONDecodeError:
                            return text_content.text
                return result.content
        except Exception as e:
            logger.error(f"MCP GitHub tool call failed: {tool_name} - {e}")
            raise
    
    # =========================================================================
    # Calendly MCP
    # =========================================================================
    
    @asynccontextmanager
    async def get_calendly_session(self, user_id: str | None = None):
        """Get or create a Calendly MCP session.
        
        Args:
            user_id: Optional user ID to fetch OAuth token for
        """
        if not settings.mcp_enabled:
            raise RuntimeError("MCP is disabled")
        
        # Get token from TokenService if user_id provided
        token = None
        if user_id:
            from src.services.token_service import token_service
            token = await token_service.get_token(user_id, "calendly")
            if token:
                logger.debug(f"Using OAuth token for user {user_id} (Calendly)")
        
        # Fall back to environment variable
        if not token:
            token = settings.calendly_api_key
            logger.debug("Using fallback API key for Calendly")
        
        if not token:
            raise RuntimeError("No Calendly token available - connect Calendly or set CALENDLY_API_KEY")
        
        python_executable = sys.executable
        
        server_params = StdioServerParameters(
            command=python_executable,
            args=["-m", "src.mcp_servers.calendly_server"],
            env={
                "CALENDLY_API_KEY": token,
            },
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session
    
    async def call_calendly_tool(
        self, 
        tool_name: str, 
        arguments: dict[str, Any],
        user_id: str | None = None
    ) -> Any:
        """Call a Calendly MCP tool.
        
        Args:
            tool_name: Name of the MCP tool to call
            arguments: Tool arguments as a dictionary
            user_id: Optional user ID for per-user OAuth token
        """
        try:
            async with self.get_calendly_session(user_id=user_id) as session:
                result = await session.call_tool(tool_name, arguments)
                
                if result.content and len(result.content) > 0:
                    text_content = result.content[0]
                    if hasattr(text_content, 'text'):
                        try:
                            return json.loads(text_content.text)
                        except json.JSONDecodeError:
                            return text_content.text
                return result.content
        except Exception as e:
            logger.error(f"MCP Calendly tool call failed: {tool_name} - {e}")
            raise
    
    # =========================================================================
    # Notion MCP
    # =========================================================================
    
    @asynccontextmanager
    async def get_notion_session(self, user_id: str | None = None):
        """Get or create a Notion MCP session.
        
        Args:
            user_id: Optional user ID to fetch OAuth token for
        """
        if not settings.mcp_enabled:
            raise RuntimeError("MCP is disabled")
        
        # Get token from TokenService if user_id provided
        token = None
        if user_id:
            from src.services.token_service import token_service
            token = await token_service.get_token(user_id, "notion")
            if token:
                logger.debug(f"Using OAuth token for user {user_id} (Notion)")
        
        # Fall back to environment variable
        if not token:
            token = settings.notion_token
            logger.debug("Using fallback token for Notion")
        
        if not token:
            raise RuntimeError("No Notion token available - connect Notion or set NOTION_TOKEN")
        
        # Import here to avoid circular imports
        from src.tools.notion import get_timeline_database_id
        
        python_executable = sys.executable
        
        server_params = StdioServerParameters(
            command=python_executable,
            args=["-m", "src.mcp_servers.notion_server"],
            env={
                "NOTION_TOKEN": token,
                "NOTION_TIMELINE_DATABASE_ID": get_timeline_database_id(),
            },
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session
    
    async def call_notion_tool(
        self, 
        tool_name: str, 
        arguments: dict[str, Any],
        user_id: str | None = None
    ) -> Any:
        """Call a Notion MCP tool.
        
        Args:
            tool_name: Name of the MCP tool to call
            arguments: Tool arguments as a dictionary
            user_id: Optional user ID for per-user OAuth token
        """
        try:
            async with self.get_notion_session(user_id=user_id) as session:
                result = await session.call_tool(tool_name, arguments)
                
                if result.content and len(result.content) > 0:
                    text_content = result.content[0]
                    if hasattr(text_content, 'text'):
                        try:
                            return json.loads(text_content.text)
                        except json.JSONDecodeError:
                            return text_content.text
                return result.content
        except Exception as e:
            logger.error(f"MCP Notion tool call failed: {tool_name} - {e}")
            raise
    
    # =========================================================================
    # Google Docs MCP
    # =========================================================================
    
    @asynccontextmanager
    async def get_google_docs_session(self):
        """Get or create a Google Docs MCP session."""
        if not settings.mcp_enabled:
            raise RuntimeError("MCP is disabled")
        
        python_executable = sys.executable
        
        server_params = StdioServerParameters(
            command=python_executable,
            args=["-m", "src.mcp_servers.google_docs_server"],
            env={
                "GOOGLE_SERVICE_ACCOUNT_JSON": settings.google_service_account_json,
            },
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session
    
    async def call_google_docs_tool(
        self, 
        tool_name: str, 
        arguments: dict[str, Any]
    ) -> Any:
        """Call a Google Docs MCP tool."""
        try:
            async with self.get_google_docs_session() as session:
                result = await session.call_tool(tool_name, arguments)
                
                if result.content and len(result.content) > 0:
                    text_content = result.content[0]
                    if hasattr(text_content, 'text'):
                        try:
                            return json.loads(text_content.text)
                        except json.JSONDecodeError:
                            return text_content.text
                return result.content
        except Exception as e:
            logger.error(f"MCP Google Docs tool call failed: {tool_name} - {e}")
            raise


# Global singleton instance
mcp_client = MCPClientManager()


@asynccontextmanager
async def mcp_lifespan():
    """FastAPI lifespan context manager for MCP client."""
    await mcp_client.start()
    try:
        yield
    finally:
        await mcp_client.stop()
