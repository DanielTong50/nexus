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

### Pattern
```python
@tool
async def log_partnership_status(
    event_name: str,
    partner_name: str,
    category: str,
    status: str
) -> str:
    """Update partnership status in Google Sheet.
   
    Args:
        event_name: Name of the event (e.g., "Blueprint")
        partner_name: Company or person name
        category: One of: Sponsors, Judges, Mentors, StudentMentors
        status: One of: pending, verbal confirmation, secured, rejected
    """
    try:
        # implementation
        return f"Updated {partner_name} to {status}"
    except Exception as e:
        return f"Failed to update: {str(e)}"
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
│   ├── settings.py      # Pydantic Settings class
│   ├── prompts.py       # All LLM prompts
│   └── tool_schemas.py  # Tool definitions
├── src/
│   ├── agents/          # One file per agent
│   ├── graph/           # LangGraph workflow
│   ├── tools/           # One file per external service
│   ├── services/        # Database, auth
│   └── models/          # Pydantic models
└── tests/
```

## Common Mistakes to Avoid
- Don't use `requests` - use `httpx` (async)
- Don't hardcode strings that might change
- Don't return raw dicts from agents
- Don't forget to await async functions
- Don't put business logic in route handlers
