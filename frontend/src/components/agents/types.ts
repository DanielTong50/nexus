/**
 * Type definitions for the Agent Progress UI
 * 
 * These types define the structure for the Cursor-style agent progress feed
 * with task cards, progress steps, and file editing indicators.
 */

import { AGENTS, AgentId } from "@/lib/config";

// Agent task status - matches the visual states in the UI
export type AgentTaskStatus = 'thinking' | 'executing' | 'analyzing' | 'complete' | 'error';

// File type for icon mapping
export type FileIconType = 'document' | 'code' | 'config' | 'walkthrough' | 'task';

// Individual progress step within a task
export interface ProgressStep {
    id: string;
    stepNumber: number;
    description: string;
    status: 'pending' | 'running' | 'complete';
    expandedContent?: string;  // Optional detailed breakdown
}

// Files that an agent is editing
export interface EditedFile {
    filename: string;
    icon: FileIconType;
    path: string;
}

// Complete agent task card data
export interface AgentTask {
    id: string;
    agentId: AgentId;
    agentName: string;
    taskTitle: string;
    taskDescription: string;
    status: AgentTaskStatus;
    statusMessage: string;           // Dynamic status text shown inline (e.g., "Starting task execution...")
    thinkingTime?: string;          // "7s" - displayed as "Thought for 7s"
    thinkingContent?: string;       // Expandable reasoning content
    filesEdited: EditedFile[];
    progressSteps: ProgressStep[];
    toolCalls: string[];            // List of tool names used (for "Tools used" section)
    completionMessage?: string;     // Final summary message
    timestamp: string;
}

// User message in the feed
export interface UserMessage {
    id: string;
    content: string;
    timestamp: string;
}

// Union type for feed items
export type FeedItem =
    | { type: 'user'; data: UserMessage }
    | { type: 'agent'; data: AgentTask };

// Tool call from backend (for mapping to progress steps)
export interface ToolCallEvent {
    toolName: string;
    status: 'pending' | 'success' | 'error';
    input?: string;
    output?: string;
}

// Agent icon names matching lucide-react (same as navbar)
export const AGENT_ICON_NAMES: Record<AgentId, string> = {
    partnerships: 'Handshake',
    marketing: 'Megaphone',
    finance: 'DollarSign',
    events: 'Calendar',
    developers: 'Code',
};

// Router/System agent icon
export const ROUTER_ICON_NAME = 'Sparkles';

// Get agent display info from ID
export function getAgentInfo(agentId: AgentId) {
    return {
        ...AGENTS[agentId],
        iconName: AGENT_ICON_NAMES[agentId],
    };
}

// Map file extension to icon type
export function getFileIconType(filename: string): FileIconType {
    const ext = filename.split('.').pop()?.toLowerCase();

    if (filename.includes('walkthrough')) return 'walkthrough';
    if (filename.includes('task')) return 'task';

    switch (ext) {
        case 'py':
        case 'ts':
        case 'tsx':
        case 'js':
        case 'jsx':
            return 'code';
        case 'json':
        case 'yaml':
        case 'yml':
        case 'env':
        case 'toml':
            return 'config';
        default:
            return 'document';
    }
}

// Status display text mapping
export const STATUS_TEXT: Record<AgentTaskStatus, string> = {
    thinking: 'Thinking...',
    executing: 'Executing...',
    analyzing: 'Analyzing...',
    complete: 'Complete',
    error: 'Error',
};
