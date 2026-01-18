# Nexus Project Rules

## What We're Building
AI-native event production platform with 5 agents (Partnerships, Marketing, Finance, Events, Developers) that execute tasks in parallel.

## Architecture Overview
- Backend: FastAPI + LangGraph (async, parallel agent execution)
- Frontend: Next.js + ShadCN
- Database: MongoDB Atlas
- LLMs: Gemini 3 Pro (classifier), Gemini 3 Flash (agents)
- Deploy: DigitalOcean App Platform

## Key Files
- `HIGH_LEVEL_PROJECT_DOC.md` - Agent tools and workflows
- `TECHNICAL_ARCHITECTURE.md` - System design and folder structure
- `backend.md` - Backend coding standards
- `frontend.md` - Frontend coding standards

## Config-Driven Development
NEVER hardcode:
- API keys → `.env`
- Model names → `config/settings.py`
- Prompts → `config/prompts.py`
- Colors → `lib/config.ts`
- Thresholds → `config/settings.py`

## Team Split
Backend Dev 1: Graph, classifier, router, error handling
Backend Dev 2: Agents, tools, HITL logic
Frontend Dev 1: Navbar, views, event filter
Frontend Dev 2: Chat panel, agent feed, approval modal

## Testing Requirements
- Backend: pytest + pytest-asyncio, mock external APIs with respx
- Frontend: Manual testing + component tests

## Git Workflow
- Branch naming: `feat/agent-partnerships`, `fix/sse-connection`
- Commit format: `feat(agents): add partnerships tools`
- PR required for main branch

## When Stuck
1. Check the architecture doc first
2. Check if there's a similar pattern in existing code
3. Ask teammate working on related area
