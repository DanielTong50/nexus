# Nexus Frontend Rules

## Project Context
Dashboard for AI event production platform. Left navbar with agent views, collapsible chat panel with Cursor-style agent feed.

## Tech Stack
- Next.js 14 (App Router)
- ShadCN UI components
- TypeScript (strict mode)

## Design System

### Colors (from config)
```typescript
// lib/config.ts
export const colors = {
  primary: '#334155',     // slate-700
  secondary: '#e2e8f0',   // slate-200
  background: '#f8fafc',  // slate-50
}
```

### Rules
- Always use colors from config, never hardcode hex values
- Use ShadCN components, don't build custom ones
- Dark mode: slate-700 background, slate-200 text
- Light mode: slate-50 background, slate-700 text

## Code Style

### TypeScript
- Strict mode enabled
- Explicit return types on functions
- Use interfaces for component props
- Use type for unions/intersections

### Pattern
```typescript
interface ChatPanelProps {
  isOpen: boolean;
  onClose: () => void;
  eventId: string;
}

export function ChatPanel({ isOpen, onClose, eventId }: ChatPanelProps) {
  // ...
}
```

### Naming
- PascalCase for components
- camelCase for functions and variables
- SCREAMING_SNAKE_CASE for constants
- Prefix hooks with `use` (e.g., `useAgentStream`)

### File Structure
```
components/
├── layout/
│   ├── Navbar.tsx
│   ├── ChatPanel.tsx
│   └── MainLayout.tsx
├── agents/
│   └── AgentFeed.tsx
├── views/
│   ├── EventsView.tsx
│   ├── PartnershipsView.tsx
│   ├── MarketingView.tsx
│   ├── FinanceView.tsx
│   └── DevelopersView.tsx
└── ui/                    # ShadCN components
```

## Component Patterns

### Layout
```typescript
// Always use flex with explicit directions
<div className="flex h-screen">
  <Navbar collapsed={chatOpen} />
  {chatOpen && <ChatPanel />}      {/* 25% width */}
  <main className="flex-1">        {/* Remaining width */}
    {children}
  </main>
</div>
```

### Chat Panel
- Fixed 25% width when open
- Input box at bottom
- Agent feed scrolls above input
- Smooth collapse/expand animation

### Agent Feed (Cursor-style)
- Stream updates as they arrive
- Show agent name + current action
- Tool calls displayed with spinner while executing
- Document links clickable (open in new tab)

### Pattern
```typescript
interface AgentUpdate {
  agentName: string;
  status: 'thinking' | 'executing' | 'complete' | 'error';
  message: string;
  documentLink?: string;  // If present, make clickable
}
```

## State Management

### Rules
- Use React state for UI-only state
- Use URL params for filterable state (event selection)
- SSE for real-time agent updates

### SSE Pattern
```typescript
function useAgentStream(onUpdate: (update: AgentUpdate) => void) {
  useEffect(() => {
    const eventSource = new EventSource('/api/chat/stream');
    eventSource.onmessage = (e) => {
      const update = JSON.parse(e.data);
      onUpdate(update);
    };
    return () => eventSource.close();
  }, []);
}
```

## API Integration

### Pattern
```typescript
// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL;

export async function sendChatMessage(message: string, eventId: string) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, event_id: eventId }),
  });
  return res.json();
}
```

### Rules
- API base URL from environment variable
- Always handle loading and error states
- Use try/catch, display user-friendly errors

## Accessibility
- All interactive elements focusable
- Keyboard navigation in navbar
- ARIA labels on icon-only buttons
- Focus trap in modals

## Common Mistakes to Avoid
- Don't hardcode colors - use config
- Don't use `any` type
- Don't forget loading states
- Don't forget to close SSE connections on unmount
- Don't use inline styles - use Tailwind classese

