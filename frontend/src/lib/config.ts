/**
 * Nexus Frontend Configuration
 *
 * This file contains all configuration values for the frontend application.
 * Environment variables are loaded from .env.local in development.
 */

// API Configuration
export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export const API_BASE = `${API_URL}/api`;

// API Endpoints
export const ENDPOINTS = {
  // Chat endpoints
  chat: `${API_BASE}/chat`,
  chatStream: `${API_BASE}/chat/stream`,

  // Approval endpoints
  approve: `${API_BASE}/approve`,
  approvals: `${API_BASE}/approvals`,

  // Info endpoints
  agents: `${API_BASE}/agents`,
  config: `${API_BASE}/config`,
  health: `${API_URL}/health`,
} as const;

// Agent Configuration
export const AGENTS = {
  partnerships: {
    id: "partnerships",
    name: "Partnerships",
    description: "Sponsor outreach and partner management",
    color: "hsl(var(--agent-partnerships))",
    icon: "Handshake",
  },
  marketing: {
    id: "marketing",
    name: "Marketing",
    description: "Social media and content creation",
    color: "hsl(var(--agent-marketing))",
    icon: "Megaphone",
  },
  finance: {
    id: "finance",
    name: "Finance",
    description: "Budget management and documentation",
    color: "hsl(var(--agent-finance))",
    icon: "DollarSign",
  },
  events: {
    id: "events",
    name: "Events",
    description: "Logistics and operations",
    color: "hsl(var(--agent-events))",
    icon: "Calendar",
  },
  developers: {
    id: "developers",
    name: "Developers",
    description: "Platform features and GitHub",
    color: "hsl(var(--agent-developers))",
    icon: "Code",
  },
} as const;

export type AgentId = keyof typeof AGENTS;

// Navigation Items
export const NAV_ITEMS = [
  { id: "overview", label: "Overview", href: "/overview", icon: "LayoutDashboard" },
  { id: "events", label: "Events", href: "/events", icon: "Calendar" },
  { id: "partnerships", label: "Partnerships", href: "/partnerships", icon: "Handshake" },
  { id: "marketing", label: "Marketing", href: "/marketing", icon: "Megaphone" },
  { id: "finance", label: "Finance", href: "/finance", icon: "DollarSign" },
  { id: "developers", label: "Developers", href: "/developers", icon: "Code" },
] as const;

// Event Filter Options (for demo)
export const EVENT_OPTIONS = [
  { value: "all", label: "All Events" },
  { value: "blueprint", label: "Blueprint" },
  { value: "hackathon", label: "Hackathon" },
  { value: "workshop", label: "Workshop Series" },
] as const;

// SSE Event Types (from backend)
export const SSE_EVENT_TYPES = {
  CLASSIFICATION: "classification",
  ROUTING: "routing",
  AGENT_START: "agent_start",
  TOOL_CALL: "tool_call",
  AGENT_COMPLETE: "agent_complete",
  APPROVAL_REQUIRED: "approval_required",
  COMPLETE: "complete",
  ERROR: "error",
} as const;

// HITL Actions that require approval
export const HITL_ACTIONS = [
  "draft_mou",
  "generate_invoice",
  "schedule_instagram_post",
  "schedule_linkedin_post",
  "announce_to_slack",
] as const;
