# Nexus Backend Rules

## Project Context
Building an AI-native event production platform with 5 specialized agents (Partnerships, Marketing, Finance, Events, Developers) that execute tasks in parallel using LangGraph.

## Tech Stack
- Python 3.12, FastAPI, LangChain, LangGraph
- MongoDB Atlas (with Vector Search), Redis
- DigitalOcean App Platform
- Package manager: uv

## Code Style

### General
- Use async/await everywhere - FastAPI and LangGraph are async-native
- Type hints required on all functions
- Use Pydantic models for all data structures
- Keep functions small and focused (< 30 lines)

### Naming
- snake_case for functions and variables
- PascalCase for classes
- SCREAMING_SNAKE_CASE for constants
- Prefix async functions with verb (e.g., `async def fetch_sponsor()`)

### Imports
```python
# Standard library
from typing import List, Optional
import asyncio

# Third party
from fastapi import APIRouter
from langchain_core.tools import tool
from pydantic import BaseModel

# Local
from config.settings import settings
from src.models.state import GraphState
```

## Architecture Rules

### Config-Driven Design
- ALL configurable values go in `config/settings.py`
- ALL LLM prompts go in `config/prompts.py`
- Never hardcode API keys, URLs, thresholds, or prompts

### Agents
- Each agent inherits from `BaseAgent` in `src/agents/base.py`
- Agents only call tools, never external APIs directly
- Agent methods must be async
- Return structured Pydantic models, not dicts

### Tools
- Tools go in `src/tools/` organized by service
- Use `@tool` decorator from langchain_core
- Include docstring with clear description for LLM
- Handle errors gracefully - return error message, don't raise
- **Tools call MCP client, not external APIs directly**

### Tool Pattern (using MCP)
```python
from src.services.mcp_client import mcp_client

@tool
async def log_partnership(
    sheet_name: str,
    company: str,
    status: str
) -> str:
    """Add partnership entry to Google Sheet.
   
    Args:
        sheet_name: Name of the sheet (e.g., 'Boothing Companies')
        company: Company name
        status: Current status (pending, confirmed, rejected)
    """
    try:
        row = [[company, "", "", "", status, "", ""]]
        await mcp_client.call_google_sheets_tool(
            "append_row",
            {"range": f"{sheet_name}!A:G", "values": row}
        )
        return f"Added {company} to {sheet_name}"
    except Exception as e:
        return f"Failed to add: {str(e)}"
```

### MCP (Model Context Protocol)
- MCP servers go in `src/mcp_servers/` - one per external service
- MCP client in `src/services/mcp_client.py` manages server lifecycle
- Servers use stdio transport (spawned as subprocesses)
- Toggle with `mcp_enabled` setting

### MCP Server Pattern
```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("my-service-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [Tool(name="my_tool", description="...", inputSchema={...})]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    # Execute tool and return result
    return [TextContent(type="text", text=json.dumps(result))]
```

### MCP Client Usage
```python
from src.services.mcp_client import mcp_client

# Call MCP tool
result = await mcp_client.call_google_sheets_tool("read_range", {"range": "Sheet1!A:G"})
```

### Graph (LangGraph)
- Graph definition in `src/graph/workflow.py`
- Use typed state with `TypedDict` or Pydantic
- Parallel execution via conditional edges to multiple nodes
- Always include error handling node

### API Endpoints
- Use `APIRouter` from FastAPI
- SSE streaming via `sse_starlette`
- All endpoints return Pydantic models
- Include request validation

## LLM Usage

### Models
- Classifier: `gemini-3-pro` (accuracy matters)
- Agents: `gemini-3-flash` (speed matters)
- Get model name from `settings.classifier_model` / `settings.agent_model`

### Prompts
- Store in `config/prompts.py` as module-level constants
- Use f-strings with named placeholders
- Keep prompts concise but explicit

## Error Handling

### Pattern
```python
async def with_retry(func, max_retries=2):
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries:
                return AgentError(message=str(e), agent=func.__name__)
            await asyncio.sleep(1 * (attempt + 1))
```

### Rules
- Never let exceptions bubble up unhandled
- Log all errors with context
- Return structured error objects, not strings
- Retry transient failures (API timeouts), not validation errors

## Testing

### Required Tests
- Unit tests for each tool (mocked external APIs)
- Unit tests for classifier and router
- Integration test for full graph execution

### Pattern
```python
@pytest.mark.asyncio
async def test_log_partnership_status():
    with respx.mock:
        respx.post("https://sheets.googleapis.com/...").respond(200)
        result = await log_partnership_status("Blueprint", "Google", "Sponsors", "secured")
        assert "Updated" in result
```

## File Organization
```
backend/
├── config/
│   ├── settings.py      # Pydantic Settings (mcp_enabled, etc.)
│   ├── prompts.py       # All LLM prompts
│   └── tool_schemas.py  # Tool definitions
├── src/
│   ├── agents/          # One file per agent
│   ├── graph/           # LangGraph workflow
│   ├── tools/           # LangChain tools (call MCP client)
│   ├── mcp_servers/     # MCP server implementations
│   │   └── google_sheets_server.py
│   ├── services/
│   │   ├── mcp_client.py  # MCP client manager
│   │   ├── database.py
│   │   └── auth.py
│   └── models/          # Pydantic models
└── tests/
```

## Common Mistakes to Avoid
- Don't use `requests` - use `httpx` (async)
- Don't hardcode strings that might change
- Don't return raw dicts from agents
- Don't forget to await async functions
- Don't put business logic in route handlers
- Don't call external APIs directly from tools - use MCP client
- Don't forget to check `mcp_enabled` setting before MCP calls
