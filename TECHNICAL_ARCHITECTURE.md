Nexus - Technical Architecture Document (copy and paste in terminal to see a better view of the system architecture diagram.

Tech Stack

Backend: Python 3.12, FastAPI, LangChain + LangGraph
Frontend: Next.js 14, ShadCN UI
Database: MongoDB Atlas (with Vector Search)
Message Queue: Redis (for real-time streaming)
Hosting: DigitalOcean App Platform
Package Manager: uv

Design Decisions

LLM Provider:
- Classifier: Gemini 3 Pro (accurate intent classification)
- Agents: Gemini 3 Flash (fast, cheap, parallel-friendly)

Real-Time UI: Server-Sent Events (SSE) via FastAPI StreamingResponse

State Persistence: In-memory for hackathon MVP, add Redis persistence later

Parallel Agent Execution

No multiple VMs needed. LangGraph runs all agents in parallel via asyncio.gather() in a single process.

DigitalOcean Setup:
- Deploy as single web service
- FastAPI runs with uvicorn (async native)
- For heavy load: scale horizontally (App Platform auto-scales instances)

System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (Next.js)                        │
│  ┌──────────────┐  ┌──────────────────────────┐  ┌──────────────┐  │
│  │ Left Navbar  │  │ Chat Panel (25% width)   │  │ Main Content │  │
│  │ - Events     │  │ - Input box              │  │ (Agent View) │  │
│  │ - Partner    │  │ - Agent feed (Cursor-    │  │              │  │
│  │ - Marketing  │  │   style with clickable   │  │              │  │
│  │ - Finance    │  │   doc links)             │  │              │  │
│  │ - Events     │  │                          │  │              │  │
│  │ - Developers │  └──────────────────────────┘  │              │  │
│  │ [Chat btn]   │                                │              │  │
│  └──────────────┘                                └──────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼ HTTP POST + SSE Stream
┌─────────────────────────────────────────────────────────────────────┐
│                          BACKEND (FastAPI)                          │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                      CLASSIFIER NODE                           │ │
│  │  Input: "Just finished meeting with Google..."                 │ │
│  │  Output: {type: "status_update", sub_prompts: [...]}           │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                │                                    │
│                                ▼                                    │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                       ROUTER NODE                              │ │
│  │  Maps sub_prompts → agent assignments                          │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                │                                    │
│         ┌──────────┬──────────┼──────────┬──────────┐              │
│         ▼          ▼          ▼          ▼          ▼              │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│  │Partnership│ │ Marketing │ │  Finance  │ │  Events   │ │Developers │
│  │  Agent    │ │  Agent    │ │  Agent    │ │  Agent    │ │  Agent    │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘
│         │          │          │          │          │              │
│         └──────────┴──────────┼──────────┴──────────┘              │
│                               ▼                                    │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    VALIDATION LAYER                            │ │
│  │  - Check if action needs approval (HITL)                       │ │
│  │  - Validate outputs                                            │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                               │                                    │
│                               ▼                                    │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                    ERROR HANDLER                               │ │
│  │  - Retry (max 2 attempts)                                      │ │
│  │  - Fallback: alert user                                        │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES                           │
│  Google Sheets │ Slack │ Figma │ GitHub │ Calendly │ LinkedIn      │
└─────────────────────────────────────────────────────────────────────┘
```

LangGraph Flow

```
         START
           │
           ▼
      ┌─────────┐
      │Classifier│ (Gemini 3 Pro)
      └────┬────┘
           ▼
      ┌─────────┐
      │ Router  │
      └────┬────┘
           │
    ┌──────┼──────┐
    ▼      ▼      ▼
 Agent1  Agent2  AgentN  (parallel, Gemini 3 Flash)
    │      │      │
    ▼      ▼      ▼
 Validate Validate Validate
    │      │      │
    └──────┼──────┘
           ▼
      ┌─────────┐
      │Aggregator│
      └────┬────┘
           ▼
      ┌─────────┐
      │  HITL?  │──Yes──→ Wait for approval
      └────┬────┘
           │ No
           ▼
       Execute
           │
           ▼
          END
```

Frontend Layout

Left Navigation Bar:
- Events (view current/past events of the year)
- Partnerships (money raised, judges count, sponsor status — filterable by event)
- Marketing (campaigns, posts, engagement stats — filterable by event)
- Finance (budget status, invoices, MOUs — filterable by event)
- Events/Logistics (venue, food, schedule — filterable by event)
- Developers (issues, PRs, repo activity — filterable by event)
- [Chat button at bottom]

Chat Interaction:
1. User clicks Chat button
2. Navbar collapses to icon-only mode
3. Chat panel appears (25% screen width) to the LEFT of main content with:
   - Input box at bottom
   - Agent feed above (Cursor-style)
4. Main content (agent view) remains on the RIGHT

Agent Feed (Cursor-style):
- Shows text updates as agents "think"
- Displays tool calls being made (e.g., "Updating Google Sheet...")
- Document links are clickable — opens the actual doc (Google Sheet, Slack, etc.)
- Cannot preview docs inline, but clicking opens them in new tab

Demo Workflow

Prompt: "Just finished a meeting with a sponsor, Google, who agreed to pay $1,000 in exchange for boothing at Blueprint."

Agents execute in parallel:

1. Partnerships Agent:
   - log_partnership_status → Updates Google Sheet with "verbal confirmation"

2. Finance Agent:
   - draft_mou → Generates MOU (queued for approval)
   - generate_invoice → Creates invoice (queued for approval)

3. Marketing Agent:
   - update_sponsor_in_content → Updates marketing files, flags posts needing sponsor info

4. Events Agent:
   - update_logistics_sheet → Adds Google to boothing schedule
   - announce_to_slack → Posts "New sponsor confirmed" to #blueprint-team

Folder Structure

```
nexus/
├── backend/
│   ├── pyproject.toml
│   ├── .env.example
│   ├── config/
│   │   ├── settings.py         # all config values
│   │   ├── prompts.py          # all LLM prompts
│   │   └── tool_schemas.py     # tool definitions
│   ├── src/
│   │   ├── main.py             # FastAPI entry
│   │   ├── api/
│   │   │   ├── routes.py       # /chat, /approve endpoints
│   │   │   └── streaming.py    # SSE logic
│   │   ├── agents/
│   │   │   ├── base.py
│   │   │   ├── partnerships.py
│   │   │   ├── marketing.py
│   │   │   ├── finance.py
│   │   │   ├── events.py
│   │   │   └── developers.py
│   │   ├── graph/
│   │   │   ├── classifier.py
│   │   │   ├── router.py
│   │   │   ├── workflow.py     # LangGraph definition
│   │   │   └── error_handler.py
│   │   ├── tools/
│   │   │   ├── google_sheets.py
│   │   │   ├── slack.py
│   │   │   ├── figma.py
│   │   │   ├── github.py
│   │   │   ├── calendly.py
│   │   │   └── social.py
│   │   ├── services/
│   │   │   ├── database.py
│   │   │   └── auth.py
│   │   └── models/
│   │       ├── state.py
│   │       └── requests.py
│   └── tests/
│       ├── test_classifier.py
│       ├── test_router.py
│       ├── test_agents/
│       └── test_tools/
├── frontend/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Navbar.tsx
│   │   │   └── ChatPanel.tsx
│   │   ├── agents/
│   │   │   └── AgentFeed.tsx   # Cursor-style feed
│   │   └── views/
│   │       ├── EventsView.tsx
│   │       ├── PartnershipsView.tsx
│   │       ├── MarketingView.tsx
│   │       ├── FinanceView.tsx
│   │       └── DevelopersView.tsx
│   └── lib/
│       └── config.ts           # colors, API urls
└── README.md
```

Testing Checkpoints

Backend Developer 1 (Graph & Routing):
1. Classifier correctly categorizes prompts
2. Router splits into correct sub-prompts
3. Parallel execution runs faster than sequential
4. Error handler retries and falls back correctly

Backend Developer 2 (Agents & Tools):
1. Each tool makes correct API calls (mocked)
2. Each agent selects correct tools for prompts
3. HITL triggers for high-stakes actions
4. Validation catches malformed outputs

Frontend Developer 1 (Navbar & Views):
1. Navbar navigation works, shows correct view
2. Event filter works across all views
3. Stats display correctly per agent view
4. Chat button collapses navbar

Frontend Developer 2 (Chat & Agent Feed):
1. Chat sends message to backend
2. SSE stream displays agent updates in real-time
3. Document links in feed are clickable and open correct URL
4. Approval modal appears for HITL actions

Dependencies

Backend (pyproject.toml):
- fastapi >= 0.115.0
- uvicorn >= 0.32.0
- langchain >= 0.3.0
- langgraph >= 0.2.0
- langchain-google-genai >= 2.0.0
- pydantic >= 2.9.0
- pydantic-settings >= 2.6.0
- motor >= 3.6.0 (async MongoDB)
- redis >= 5.2.0
- httpx >= 0.28.0
- sse-starlette >= 2.1.0
- pytest >= 8.3.0
- pytest-asyncio >= 0.24.0

Frontend:
- next >= 14.0.0
- shadcn/ui components
- Colors: slate-700 (#334155), slate-200 (#e2e8f0), slate-50 (#f8fafc)


