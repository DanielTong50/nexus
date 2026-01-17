Nexus Team Collaboration Guide

TEAM ROLES

Backend Dev 1 (TBD): Graph, Classifier, Router, Error Handler, API Endpoints, Database
Backend Dev 2 (TBD): Agents, Tools, HITL Logic, Auth
Frontend Dev 1 (TBD): Navbar, Views, Event Filter, Config  - Darius
Frontend Dev 2 (TBD): Chat Panel, Agent Feed, Approval Modal

GIT BRANCH STRATEGY

Branch Types:
• main — Production-ready code only
• dev — Integration branch (merge PRs here first)
• feat/[area]-[desc] — New features
• fix/[area]-[desc] — Bug fixes
• docs/[desc] — Documentation only

Branch Examples:
• feat/backend-classifier
• feat/backend-partnerships-agent
• feat/frontend-navbar
• feat/frontend-chat-panel
• fix/backend-sse-timeout

PHASE 1: PROJECT SETUP (Day 1, Aim to finish by 1:00PM)

All team members together:
1. One person creates the repo and pushes initial structure
2. Create dev branch from main
3. Everyone clones and creates their feature branch from dev

Backend Dev 1
• Branch: feat/backend-core-setup
• Create:
  - pyproject.toml (dependencies)
  - .env.example
  - config/settings.py
  - config/prompts.py (placeholder)
  - src/main.py (FastAPI app)
  - src/api/routes.py (skeleton)
  - src/api/streaming.py (skeleton)
  - src/services/database.py (MongoDB connection)
  - src/models/state.py (LangGraph state schema)
  - src/models/requests.py (API models)
  - src/graph/workflow.py (skeleton)
• PR when: FastAPI app runs, MongoDB connects

Backend Dev 2
• Branch: feat/backend-agents-setup
• Create:
  - config/tool_schemas.py
  - src/agents/base.py
  - src/agents/partnerships.py (skeleton)
  - src/agents/marketing.py (skeleton)
  - src/agents/finance.py (skeleton)
  - src/agents/events.py (skeleton)
  - src/agents/developers.py (skeleton)
  - src/services/auth.py (user identity)
  - src/tools/ folder with all tool files (skeletons)
• PR when: Base agent class defined, auth returns user identity

Frontend Dev 1
• Branch: feat/frontend-layout-setup
• Create:
  - Next.js app with ShadCN
  - lib/config.ts (colors, API URL)
  - components/layout/Navbar.tsx (skeleton)
  - components/views/EventsView.tsx (skeleton)
  - components/views/PartnershipsView.tsx (skeleton)
  - components/views/MarketingView.tsx (skeleton)
  - components/views/FinanceView.tsx (skeleton)
  - components/views/DevelopersView.tsx (skeleton)
• PR when: App runs, navbar displays with all nav items

Frontend Dev 2
• Branch: feat/frontend-chat-setup
• Create:
  - components/layout/ChatPanel.tsx (skeleton)
  - components/agents/AgentFeed.tsx (skeleton)
  - hooks/useAgentStream.ts (SSE hook skeleton)
• PR when: Chat panel renders





PHASE 2: CORE IMPLEMENTATION (Day 1, Aim to finish by 0:00PM)

Backend Dev 1

1. feat/backend-classifier
   Files: src/graph/classifier.py, config/prompts.py (classifier prompt)
   Task: Implement classifier node with Gemini 3 Pro
   PR when: Classifier returns correct type for 3+ test prompts

2. feat/backend-router
   Files: src/graph/router.py
   Task: Implement router node
   PR when: Router assigns prompts to correct agents

3. feat/backend-parallel
   Files: src/graph/workflow.py
   Task: Wire up parallel agent execution with asyncio.gather
   PR when: 3 mock agents run in parallel

4. feat/backend-error-handler
   Files: src/graph/error_handler.py
   Task: Implement retry (max 2) + fallback
   PR when: Retry works, fallback alerts user

5. feat/backend-api-endpoints
   Files: src/api/routes.py, src/api/streaming.py
   Task: /chat endpoint with SSE streaming, /approve endpoint
   PR when: Chat endpoint streams responses

Backend Dev 2

1. feat/backend-sheets-tool
   Files: src/tools/google_sheets.py
   Task: Google Sheets read/write tools
   PR when: Tool updates sheet successfully

2. feat/backend-slack-tool
   Files: src/tools/slack.py
   Task: Slack post tool
   PR when: Tool posts to channel

3. feat/backend-other-tools
   Files: src/tools/figma.py, src/tools/github.py, src/tools/calendly.py, src/tools/social.py
   Task: Remaining tool implementations
   PR when: Each tool makes successful API call

4. feat/backend-partnerships-agent
   Files: src/agents/partnerships.py, config/prompts.py (agent prompt)
   Task: Partnerships agent with tools
   PR when: Agent handles "log sponsor" prompt

5. feat/backend-finance-agent
   Files: src/agents/finance.py
   Task: Finance agent with tools
   PR when: Agent generates MOU draft

6. feat/backend-events-agent
   Files: src/agents/events.py
   Task: Events agent with tools
   PR when: Agent updates logistics sheet

7. feat/backend-marketing-agent
   Files: src/agents/marketing.py
   Task: Marketing agent with tools
   PR when: Agent updates sponsor in content

8. feat/backend-developers-agent
   Files: src/agents/developers.py
   Task: Developers agent with tools
   PR when: Agent creates GitHub issue

9. feat/backend-hitl
   Files: src/graph/workflow.py (validation layer)
   Task: HITL validation layer
   PR when: High-cost actions queue for approval


Frontend Dev 1

1. feat/frontend-navbar
   Files: components/layout/Navbar.tsx
   Task: Full navbar with all nav items, collapse logic
   PR when: Navigation works between views, collapses on chat open

2. feat/frontend-events-view
   Files: components/views/EventsView.tsx
   Task: Events view with mock data
   PR when: View renders event cards

3. feat/frontend-partnerships-view
   Files: components/views/PartnershipsView.tsx
   Task: Partnerships stats view (money raised, judges count)
   PR when: Stats display with event filter

4. feat/frontend-other-views
   Files: MarketingView.tsx, FinanceView.tsx, DevelopersView.tsx
   Task: Remaining agent views with stats
   PR when: All views render with mock data

5. feat/frontend-event-filter
   Task: Event filter dropdown (URL params)
   PR when: Filter updates all views


Frontend Dev 2

1. feat/frontend-chat-input
   Files: components/layout/ChatPanel.tsx
   Task: Chat input with send button
   PR when: Message sends to backend

2. feat/frontend-agent-feed
   Files: components/agents/AgentFeed.tsx
   Task: Cursor-style agent feed with clickable doc links
   PR when: Updates stream in real-time

3. feat/frontend-sse-hook
   Files: hooks/useAgentStream.ts
   Task: SSE connection hook
   PR when: Hook connects and receives updates

4. feat/frontend-approval-modal
   Task: Approval modal for HITL actions
   PR when: Modal shows pending actions, approve/edit buttons work








PHASE 3: INTEGRATION (Day 2, Aim to finish by 3:00 AM)

1. feat/integration-backend (Backend Dev 1 + 2)
   Merge all backend branches to dev, test full flow

2. feat/integration-frontend (Frontend Dev 1 + 2)
   Merge all frontend branches to dev, test UI

3. feat/integration-e2e (All)
   Connect frontend to backend, full demo flow

PR RULES

Before Opening PR:
1. Run tests: pytest (backend) or build check (frontend)
2. Self-review diff for debug code, console.logs, hardcoded values
3. Ensure your branch is up-to-date with dev

PR Template:
• What: [One sentence describing what this PR does]
• How to Test: [Steps to verify this works]
• Checklist: Tests pass, no hardcoded values, config values in settings.py/config.ts

Review Process:
• PRs need 1 approval from teammate in same area (backend/frontend)
• Reviewer tests locally before approving
• Merge to dev, not main
• main only updated at end of each phase

EVERY 2 HOUR SYNC

5-minute standup:
1. What did you finish?
2. What are you working on?
3. Are you blocked?

End of day:
• Push all work (even WIP)
• Open draft PRs for visibility
• Update team on Slack




PERSONAL CONFLICT RESOLUTION

Shared files to coordinate on:
• config/settings.py — coordinate additions
• config/prompts.py — coordinate additions
• lib/config.ts — coordinate additions

If two people need to edit the same file:
1. Communicate on Slack before starting
2. One person makes changes first, opens PR
3. Other person rebases after merge

EMERGENCY FIXES

If something breaks on dev:
1. Create fix/[area]-[desc] branch from dev
2. Fix the issue
3. Open PR with "URGENT" in title
4. Get quick review and merge



