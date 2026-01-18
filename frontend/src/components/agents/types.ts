/**
 * Type definitions for the Agent Progress UI
 * 
 * These types define the structure for the Cursor-style agent progress feed
 * with task cards, progress steps, and file editing indicators.
 * 
 * Phase 4: Added task-based orchestration types for displaying task breakdown.
 */

import { AGENTS, AgentId } from "@/lib/config";

// Agent task status - matches the visual states in the UI
export type AgentTaskStatus = 'thinking' | 'executing' | 'analyzing' | 'complete' | 'error';

// Task execution status for individual tasks in a plan
export type TaskExecutionStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped' | 'approval_required';

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

// Assistant/Agent message in the feed (shown as chat bubble)
export interface AssistantMessage {
    id: string;
    agentName: string;
    content: string;
    timestamp: string;
}

// Union type for feed items
export type FeedItem =
    | { type: 'user'; data: UserMessage }
    | { type: 'assistant'; data: AssistantMessage }
    | { type: 'agent'; data: AgentTask }
    | { type: 'task_plan'; data: TaskPlanFeedItem };

// Tool call from backend (for mapping to progress steps)
export interface ToolCallEvent {
    toolName: string;
    status: 'pending' | 'success' | 'error';
    input?: string;
    output?: string;
}

// =============================================================================
// Task-based orchestration types (Phase 4)
// =============================================================================

// Extracted entity from user message
export interface ExtractedEntity {
    type: string;
    value: string | number;
    confidence?: number;
}

// Individual task in a task plan
export interface TaskInfo {
    id: string;
    agent: AgentId | string;
    action: string;
    description: string;
    depends_on: string[];
    requires_approval: boolean;
    status: TaskExecutionStatus;
    result?: string;
    error?: string;
    execution_time?: number;
}

// Complete task plan from the backend
export interface TaskPlanData {
    plan_id: string;
    request_type: 'workflow' | 'question' | 'status_update';
    total_tasks: number;
    execution_strategy: 'sequential' | 'parallel' | 'mixed';
    target_agents: string[];
    tasks: TaskInfo[];
    extracted_entities: ExtractedEntity[];
}

// Task plan feed item for the UI
export interface TaskPlanFeedItem {
    id: string;
    plan: TaskPlanData;
    status: 'planning' | 'executing' | 'complete' | 'error';
    completedTasks: number;
    failedTasks: number;
    timestamp: string;
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

// Task execution status display text
export const TASK_STATUS_TEXT: Record<TaskExecutionStatus, string> = {
    pending: 'Pending',
    running: 'Running',
    completed: 'Completed',
    failed: 'Failed',
    skipped: 'Skipped',
    approval_required: 'Needs Approval',
};

// Task execution status colors
export const TASK_STATUS_COLORS: Record<TaskExecutionStatus, string> = {
    pending: 'text-slate-400',
    running: 'text-blue-500',
    completed: 'text-emerald-500',
    failed: 'text-red-500',
    skipped: 'text-amber-500',
    approval_required: 'text-purple-500',
};

// Task execution status background colors
export const TASK_STATUS_BG: Record<TaskExecutionStatus, string> = {
    pending: 'bg-slate-100',
    running: 'bg-blue-50',
    completed: 'bg-emerald-50',
    failed: 'bg-red-50',
    skipped: 'bg-amber-50',
    approval_required: 'bg-purple-50',
};
