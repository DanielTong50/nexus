"use client";

/**
 * useAgentStream hook - SSE streaming connection to backend
 * 
 * Connects to the FastAPI backend's /api/chat/stream endpoint
 * and parses Server-Sent Events into AgentTask objects for the new UI.
 */

import { useState, useCallback, useRef } from "react";
import { ENDPOINTS, AgentId } from "@/lib/config";
import type {
    FeedItem,
    AgentTask,
    UserMessage,
    ProgressStep,
    EditedFile,
    TaskPlanData,
    TaskPlanFeedItem,
    TaskInfo,
    TaskExecutionStatus,
} from "@/components/agents/types";
import { getFileIconType } from "@/components/agents/types";

// Backend event types
interface BackendStreamEvent {
    event_type: string;
    data: Record<string, unknown>;
    agent_name?: string;
    timestamp: string;
}

export interface UseAgentStreamReturn {
    feedItems: FeedItem[];
    isStreaming: boolean;
    error: string | null;
    sendMessage: (message: string) => Promise<void>;
    clearMessages: () => void;
}

// Map agent name to agent ID
function mapAgentNameToId(name: string): AgentId {
    const lowerName = name.toLowerCase();
    if (lowerName.includes('partnership')) return 'partnerships';
    if (lowerName.includes('marketing')) return 'marketing';
    if (lowerName.includes('finance')) return 'finance';
    if (lowerName.includes('event')) return 'events';
    if (lowerName.includes('developer') || lowerName.includes('dev')) return 'developers';
    return 'partnerships'; // default fallback
}

export function useAgentStream(): UseAgentStreamReturn {
    const [feedItems, setFeedItems] = useState<FeedItem[]>([]);
    const [isStreaming, setIsStreaming] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Track current agent task being built - use Map for parallel agents
    const currentTaskRef = useRef<AgentTask | null>(null);
    const activeAgentsRef = useRef<Map<string, { task: AgentTask; startTime: number }>>(new Map());
    const currentTaskPlanRef = useRef<TaskPlanFeedItem | null>(null);
    const stepCounterRef = useRef(0);
    const idCounter = useRef(0);
    // Track agent start time for thinking time calculation (legacy single agent)
    const agentStartTimeRef = useRef<number>(0);
    // Track pending clarification context for follow-up
    const pendingClarificationRef = useRef<{
        agent_name: string;
        context: Record<string, unknown>;
        original_request: string;
    } | null>(null);
    // Track completed agent count for staggered message display
    const completedAgentCountRef = useRef(0);

    const generateId = useCallback(() => {
        idCounter.current += 1;
        return `id-${Date.now()}-${idCounter.current}`;
    }, []);

    // Process SSE events and map to new UI structure
    const processEvent = useCallback((event: BackendStreamEvent) => {
        const { event_type, data, agent_name } = event;

        switch (event_type) {
            case "classification": {
                // Create a router/classifier task
                const routerTask: AgentTask = {
                    id: generateId(),
                    agentId: 'partnerships', // Router doesn't have a specific agent
                    agentName: 'Router',
                    taskTitle: '',
                    taskDescription: '',
                    status: 'analyzing',
                    statusMessage: data.message as string,
                    filesEdited: [],
                    progressSteps: [],
                    toolCalls: [],
                    timestamp: event.timestamp,
                };
                setFeedItems(prev => [...prev, { type: 'agent', data: routerTask }]);
                break;
            }

            case "routing": {
                // Update the router task with routing info
                setFeedItems(prev => {
                    const updated = [...prev];
                    const lastItem = updated[updated.length - 1];
                    if (lastItem?.type === 'agent' && lastItem.data.agentName === 'Router') {
                        lastItem.data.statusMessage = data.message as string;
                        lastItem.data.status = 'complete';
                    }
                    return updated;
                });
                break;
            }

            // =================================================================
            // Task-based orchestration events (Phase 4)
            // =================================================================

            case "planning": {
                // Create a planner task card
                const plannerTask: AgentTask = {
                    id: generateId(),
                    agentId: 'partnerships',
                    agentName: 'Task Planner',
                    taskTitle: '',
                    taskDescription: '',
                    status: 'analyzing',
                    statusMessage: data.message as string || 'Planning tasks...',
                    filesEdited: [],
                    progressSteps: [],
                    toolCalls: [],
                    timestamp: event.timestamp,
                };
                setFeedItems(prev => [...prev, { type: 'agent', data: plannerTask }]);
                break;
            }

            case "task_plan": {
                // Create task plan feed item with full breakdown
                const tasks = (data.tasks as Array<{
                    id: string;
                    agent: string;
                    action: string;
                    description: string;
                    depends_on: string[];
                    requires_approval: boolean;
                }>).map(t => ({
                    ...t,
                    status: 'pending' as TaskExecutionStatus,
                }));

                const planData: TaskPlanData = {
                    plan_id: data.plan_id as string,
                    request_type: data.request_type as 'workflow' | 'question' | 'status_update',
                    total_tasks: data.total_tasks as number,
                    execution_strategy: data.execution_strategy as 'sequential' | 'parallel' | 'mixed',
                    target_agents: data.target_agents as string[],
                    tasks: tasks,
                    extracted_entities: (data.extracted_entities as Array<{ type: string; value: string | number }>) || [],
                };

                const taskPlanItem: TaskPlanFeedItem = {
                    id: generateId(),
                    plan: planData,
                    status: 'executing',
                    completedTasks: 0,
                    failedTasks: 0,
                    timestamp: event.timestamp,
                };

                currentTaskPlanRef.current = taskPlanItem;

                // Update the planner task to complete
                setFeedItems(prev => {
                    const updated = [...prev];
                    const lastItem = updated[updated.length - 1];
                    if (lastItem?.type === 'agent' && lastItem.data.agentName === 'Task Planner') {
                        lastItem.data.status = 'complete';
                        lastItem.data.statusMessage = `Created ${planData.total_tasks} task(s)`;
                    }
                    // Add the task plan item
                    return [...updated, { type: 'task_plan', data: taskPlanItem }];
                });
                break;
            }

            case "task_start": {
                if (!currentTaskPlanRef.current) break;

                const taskId = data.task_id as string;
                const planId = currentTaskPlanRef.current.id;

                setFeedItems(prev => {
                    const updated = [...prev];
                    const planItem = updated.find(
                        item => item.type === 'task_plan' && item.data.id === planId
                    );

                    if (planItem?.type === 'task_plan') {
                        const task = planItem.data.plan.tasks.find(t => t.id === taskId);
                        if (task) {
                            task.status = 'running';
                        }
                    }

                    return updated;
                });
                break;
            }

            case "task_complete": {
                if (!currentTaskPlanRef.current) break;

                const taskId = data.task_id as string;
                const planId = currentTaskPlanRef.current.id;
                const result = data.message as string;
                const execTime = data.execution_time as number;

                setFeedItems(prev => {
                    const updated = [...prev];
                    const planItem = updated.find(
                        item => item.type === 'task_plan' && item.data.id === planId
                    );

                    if (planItem?.type === 'task_plan') {
                        const task = planItem.data.plan.tasks.find(t => t.id === taskId);
                        if (task) {
                            task.status = 'completed';
                            task.result = result;
                            task.execution_time = execTime;
                        }
                        planItem.data.completedTasks += 1;
                    }

                    return updated;
                });
                break;
            }

            case "task_failed":
            case "task_error": {
                if (!currentTaskPlanRef.current) break;

                const taskId = data.task_id as string;
                const planId = currentTaskPlanRef.current.id;
                const errorMsg = data.error as string;

                setFeedItems(prev => {
                    const updated = [...prev];
                    const planItem = updated.find(
                        item => item.type === 'task_plan' && item.data.id === planId
                    );

                    if (planItem?.type === 'task_plan') {
                        const task = planItem.data.plan.tasks.find(t => t.id === taskId);
                        if (task) {
                            task.status = 'failed';
                            task.error = errorMsg;
                        }
                        planItem.data.failedTasks += 1;
                    }

                    return updated;
                });
                break;
            }

            case "approval_required":
            case "task_approval_required": {
                if (!currentTaskPlanRef.current) break;

                const taskId = data.task_id as string;
                const planId = currentTaskPlanRef.current.id;

                setFeedItems(prev => {
                    const updated = [...prev];
                    const planItem = updated.find(
                        item => item.type === 'task_plan' && item.data.id === planId
                    );

                    if (planItem?.type === 'task_plan') {
                        const task = planItem.data.plan.tasks.find(t => t.id === taskId);
                        if (task) {
                            task.status = 'approval_required';
                        }
                    }

                    return updated;
                });
                break;
            }

            case "orchestration_complete": {
                if (!currentTaskPlanRef.current) break;

                const planId = currentTaskPlanRef.current.id;

                setFeedItems(prev => {
                    const updated = [...prev];
                    const planItem = updated.find(
                        item => item.type === 'task_plan' && item.data.id === planId
                    );

                    if (planItem?.type === 'task_plan') {
                        planItem.data.status = 'complete';
                    }

                    return updated;
                });

                currentTaskPlanRef.current = null;
                break;
            }

            // =================================================================
            // Legacy agent events (still supported)
            // =================================================================

            case "agent_start": {
                // Create a new agent task
                const agentName = agent_name || 'Agent';
                stepCounterRef.current = 0;
                const startTime = Date.now();
                // Record start time for thinking time calculation (legacy)
                agentStartTimeRef.current = startTime;

                const agentTask: AgentTask = {
                    id: generateId(),
                    agentId: mapAgentNameToId(agentName),
                    agentName: agentName,
                    taskTitle: '',
                    taskDescription: '',
                    status: 'thinking',
                    statusMessage: 'Starting task execution...',
                    thinkingTime: '0s',
                    filesEdited: [],
                    progressSteps: [],
                    toolCalls: [],
                    timestamp: event.timestamp,
                };

                // Track in both single ref (for backward compat) and Map (for parallel)
                currentTaskRef.current = agentTask;
                activeAgentsRef.current.set(agentName, { task: agentTask, startTime });
                setFeedItems(prev => [...prev, { type: 'agent', data: agentTask }]);
                break;
            }

            case "tool_call":
            case "agent_tool_call":
            case "tool_use":
            case "function_call": {
                // Handle different possible field names for tool name
                const toolName = (data.tool_name || data.name || data.function || data.tool) as string;
                const status = data.status as 'pending' | 'success' | 'error';

                // Look up agent by name for parallel support, fall back to currentTaskRef
                const agentNameForTool = agent_name || currentTaskRef.current?.agentName;
                const activeAgentForTool = agentNameForTool ? activeAgentsRef.current.get(agentNameForTool) : null;
                const currentId = activeAgentForTool?.task.id || currentTaskRef.current?.id;

                if (!currentId) break;

                // Map tool status to step status
                const stepStatus = status === 'pending' ? 'running' : status === 'success' ? 'complete' : 'pending';

                setFeedItems(prev => {
                    const updated = [...prev];
                    const taskItem = updated.find(
                        item => item.type === 'agent' && item.data.id === currentId
                    );

                    if (taskItem?.type === 'agent') {
                        const task = taskItem.data;

                        // Track tool call in toolCalls array (for "Tools used" section)
                        if (!task.toolCalls.includes(toolName)) {
                            task.toolCalls = [...task.toolCalls, toolName];
                        }

                        // Update status message to show current tool
                        if (status === 'pending') {
                            task.statusMessage = `Executing ${formatToolName(toolName)}...`;
                        } else if (status === 'success') {
                            task.statusMessage = `Completed ${formatToolName(toolName)}`;
                        }

                        // Check if this tool call already exists in progress steps
                        const existingStepIdx = task.progressSteps.findIndex(
                            s => s.description.includes(toolName)
                        );

                        if (existingStepIdx >= 0) {
                            // Update existing step
                            task.progressSteps[existingStepIdx].status = stepStatus;
                        } else {
                            // Add new progress step
                            stepCounterRef.current += 1;
                            const newStep: ProgressStep = {
                                id: generateId(),
                                stepNumber: stepCounterRef.current,
                                description: formatToolName(toolName),
                                status: stepStatus,
                            };
                            task.progressSteps = [...task.progressSteps, newStep];
                        }

                        // Extract file info from output if available
                        if (data.output && typeof data.output === 'object') {
                            const output = data.output as Record<string, unknown>;
                            if (output.filename || output.file) {
                                const filename = (output.filename || output.file) as string;
                                const existingFile = task.filesEdited.find(f => f.filename === filename);
                                if (!existingFile) {
                                    const newFile: EditedFile = {
                                        filename,
                                        icon: getFileIconType(filename),
                                        path: (output.path || filename) as string,
                                    };
                                    task.filesEdited = [...task.filesEdited, newFile];
                                }
                            }
                        }

                        // Update task status
                        task.status = 'executing';
                    }

                    return updated;
                });
                break;
            }

            case "text_chunk":
            case "agent_update": {
                const chunk = data.content as string;

                // Look up agent by name for parallel support, fall back to currentTaskRef
                const agentNameForChunk = agent_name || currentTaskRef.current?.agentName;
                const activeAgentForChunk = agentNameForChunk ? activeAgentsRef.current.get(agentNameForChunk) : null;
                const currentId = activeAgentForChunk?.task.id || currentTaskRef.current?.id;

                if (!currentId) break;

                setFeedItems(prev => {
                    const updated = [...prev];
                    const taskItem = updated.find(
                        item => item.type === 'agent' && item.data.id === currentId
                    );

                    if (taskItem?.type === 'agent') {
                        // Append to completion message (this is the agent's response text)
                        taskItem.data.completionMessage =
                            (taskItem.data.completionMessage || '') + chunk;
                    }

                    return updated;
                });
                break;
            }

            case "agent_complete": {
                // Look up agent by name from event, fall back to currentTaskRef
                const agentName = agent_name || currentTaskRef.current?.agentName;
                if (!agentName) break;

                const activeAgent = activeAgentsRef.current.get(agentName);
                const currentId = activeAgent?.task.id || currentTaskRef.current?.id;
                const currentAgentName = agentName;
                const completeMessage = data.message as string;

                if (!currentId) break;

                // Calculate thinking time using agent-specific start time
                const startTime = activeAgent?.startTime || agentStartTimeRef.current;
                const elapsedMs = Date.now() - startTime;
                const elapsedSeconds = Math.max(1, Math.round(elapsedMs / 1000));
                const thinkingTimeStr = `${elapsedSeconds}s`;

                // Remove from active agents map
                activeAgentsRef.current.delete(agentName);

                // Update task card immediately
                setFeedItems(prev => {
                    const updated = [...prev];
                    const taskItem = updated.find(
                        item => item.type === 'agent' && item.data.id === currentId
                    );

                    if (taskItem?.type === 'agent') {
                        taskItem.data.status = 'complete';
                        taskItem.data.statusMessage = 'Task complete';
                        taskItem.data.thinkingTime = thinkingTimeStr;
                        if (completeMessage) {
                            taskItem.data.completionMessage = completeMessage;
                        }

                        // If no tool calls were tracked via events, detect from message content
                        if (taskItem.data.toolCalls.length === 0 && completeMessage) {
                            const detectedTools = detectToolsFromMessage(completeMessage);
                            if (detectedTools.length > 0) {
                                taskItem.data.toolCalls = detectedTools;
                            }
                        }

                        // Mark all progress steps as complete
                        if (taskItem.data.progressSteps.length > 0) {
                            taskItem.data.progressSteps = taskItem.data.progressSteps.map(step => ({
                                ...step,
                                status: 'complete' as const
                            }));
                        }
                    }

                    return updated;
                });

                // Add assistant message bubble with staggered delay for real-time feel
                if (completeMessage && currentAgentName !== 'Router' && currentAgentName !== 'Task Planner') {
                    // Calculate delay based on completion order (800ms between each message)
                    const delayMs = completedAgentCountRef.current * 800;
                    completedAgentCountRef.current += 1;

                    setTimeout(() => {
                        // Extract download URL if present (format: DOWNLOAD_URL:/api/files/filename.docx\n...)
                        let downloadUrl: string | undefined;
                        let downloadFilename: string | undefined;
                        let displayMessage = completeMessage;

                        // First check if the message itself contains DOWNLOAD_URL
                        if (completeMessage.startsWith('DOWNLOAD_URL:')) {
                            const lines = completeMessage.split('\n');
                            const urlLine = lines[0];
                            downloadUrl = urlLine.replace('DOWNLOAD_URL:', '').trim();
                            downloadFilename = downloadUrl.split('/').pop();
                            displayMessage = lines.slice(1).join('\n').trim();
                        }

                        // Also check tool calls for download URLs
                        const toolCalls = data.tool_calls as Array<{
                            tool_name: string;
                            output: string;
                            status: string;
                        }> | undefined;

                        if (!downloadUrl && toolCalls) {
                            for (const toolCall of toolCalls) {
                                if (toolCall.output && toolCall.output.startsWith('DOWNLOAD_URL:')) {
                                    const lines = toolCall.output.split('\n');
                                    const urlLine = lines[0];
                                    downloadUrl = urlLine.replace('DOWNLOAD_URL:', '').trim();
                                    downloadFilename = downloadUrl.split('/').pop();
                                    break;
                                }
                            }
                        }

                        setFeedItems(prev => [...prev, {
                            type: 'assistant',
                            data: {
                                id: generateId(),
                                agentName: currentAgentName,
                                content: displayMessage,
                                downloadUrl,
                                downloadFilename,
                                timestamp: event.timestamp,
                            }
                        }]);
                    }, delayMs);
                }

                currentTaskRef.current = null;
                break;
            }

            case "complete": {
                setIsStreaming(false);
                currentTaskRef.current = null;
                break;
            }

            case "error": {
                setError(data.error as string);

                if (currentTaskRef.current) {
                    const currentId = currentTaskRef.current.id;
                    setFeedItems(prev => {
                        const updated = [...prev];
                        const taskItem = updated.find(
                            item => item.type === 'agent' && item.data.id === currentId
                        );
                        if (taskItem?.type === 'agent') {
                            taskItem.data.status = 'error';
                            taskItem.data.completionMessage = `Error: ${data.error}`;
                        }
                        return updated;
                    });
                }
                break;
            }

            case "clarification_needed": {
                // Handle clarification request from agent - show as assistant message bubble
                const agentName = data.agent_name as string;
                const context = data.context as Record<string, unknown>;
                const message = data.message as string;

                // Store context for follow-up
                pendingClarificationRef.current = {
                    agent_name: agentName,
                    context: context,
                    original_request: currentTaskRef.current?.id || '',
                };

                // Use the message directly - it already contains the questions from the LLM
                // Don't append questions array as that causes duplication
                setFeedItems(prev => [...prev, {
                    type: 'assistant',
                    data: {
                        id: generateId(),
                        agentName: agentName,
                        content: message,
                        timestamp: event.timestamp,
                    }
                }]);
                break;
            }

            default:
                console.log("Unknown event type:", event_type, data);
        }
    }, [generateId]);

    // Build conversation history from feed items for context
    const buildConversationHistory = useCallback(() => {
        const history: Array<{ role: string; content: string; agent?: string }> = [];

        // Get the last 10 relevant items for context
        const relevantItems = feedItems.slice(-20);

        for (const item of relevantItems) {
            if (item.type === 'user') {
                history.push({
                    role: 'user',
                    content: item.data.content,
                });
            } else if (item.type === 'assistant') {
                history.push({
                    role: 'assistant',
                    content: item.data.content,
                    agent: item.data.agentName,
                });
            } else if (item.type === 'agent' && item.data.completionMessage) {
                history.push({
                    role: 'assistant',
                    content: item.data.completionMessage,
                    agent: item.data.agentName,
                });
            }
        }

        // Keep only the last 10 messages
        return history.slice(-10);
    }, [feedItems]);

    const sendMessage = useCallback(async (userMessage: string) => {
        if (!userMessage.trim()) return;

        setError(null);
        setIsStreaming(true);
        currentTaskRef.current = null;
        stepCounterRef.current = 0;
        completedAgentCountRef.current = 0;

        // Build conversation history before adding new message
        const conversationHistory = buildConversationHistory();

        // Add user message immediately
        const userMsg: UserMessage = {
            id: generateId(),
            content: userMessage,
            timestamp: new Date().toISOString(),
        };
        setFeedItems(prev => [...prev, { type: 'user', data: userMsg }]);

        try {
            // Build request body with conversation history and optional clarification context
            const requestBody: Record<string, unknown> = {
                message: userMessage,
                request_id: `req-${Date.now()}`,
                conversation_history: conversationHistory,
            };

            // Include clarification context if we're responding to a clarification request
            if (pendingClarificationRef.current) {
                requestBody.clarification_context = pendingClarificationRef.current;
                // Clear after sending
                pendingClarificationRef.current = null;
            }

            const response = await fetch(ENDPOINTS.chatStream, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(requestBody),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            if (!response.body) {
                throw new Error("No response body");
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();

                if (done) break;

                buffer += decoder.decode(value, { stream: true });

                // Process complete SSE messages
                const lines = buffer.split("\n");
                buffer = lines.pop() || "";

                for (const line of lines) {
                    if (line.startsWith("data:")) {
                        const jsonStr = line.slice(5).trim();
                        if (jsonStr) {
                            try {
                                const event: BackendStreamEvent = JSON.parse(jsonStr);
                                processEvent(event);
                            } catch {
                                console.warn("Failed to parse SSE event:", jsonStr);
                            }
                        }
                    }
                }
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : "Stream connection failed";
            setError(errorMessage);
            console.error("Stream error:", err);

            // Add error task
            const errorTask: AgentTask = {
                id: generateId(),
                agentId: 'partnerships',
                agentName: 'System',
                taskTitle: 'Connection Error',
                taskDescription: '',
                status: 'error',
                statusMessage: `${errorMessage}. Please check if the backend is running.`,
                filesEdited: [],
                progressSteps: [],
                toolCalls: [],
                timestamp: new Date().toISOString(),
            };
            setFeedItems(prev => [...prev, { type: 'agent', data: errorTask }]);
        } finally {
            setIsStreaming(false);
            currentTaskRef.current = null;
        }
    }, [generateId, processEvent]);

    const clearMessages = useCallback(() => {
        setFeedItems([]);
        setError(null);
        currentTaskRef.current = null;
        activeAgentsRef.current.clear();
        currentTaskPlanRef.current = null;
        stepCounterRef.current = 0;
        agentStartTimeRef.current = 0;
        completedAgentCountRef.current = 0;
        pendingClarificationRef.current = null;
    }, []);

    return {
        feedItems,
        isStreaming,
        error,
        sendMessage,
        clearMessages,
    };
}

// Helper to format tool names into human-readable descriptions
function formatToolName(toolName: string): string {
    return toolName
        .replace(/_/g, ' ')
        .replace(/([A-Z])/g, ' $1')
        .trim()
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ');
}

// Detect tools used from the completion message content
// This is a fallback when the backend doesn't send tool_call events
function detectToolsFromMessage(message: string): string[] {
    const lowerMessage = message.toLowerCase();
    const detectedTools: string[] = [];

    // Slack detection
    if (lowerMessage.includes('slack') ||
        lowerMessage.includes('channel') ||
        lowerMessage.includes('sent a message') ||
        lowerMessage.includes('message to') ||
        lowerMessage.includes('reminder')) {
        detectedTools.push('send_slack_message');
    }

    // Google Sheets detection
    if (lowerMessage.includes('spreadsheet') ||
        lowerMessage.includes('google sheets') ||
        lowerMessage.includes('logged') ||
        lowerMessage.includes('partnership')) {
        detectedTools.push('google_sheets');
    }

    // Google Docs detection
    if (lowerMessage.includes('google doc') ||
        lowerMessage.includes('document created')) {
        detectedTools.push('create_google_doc');
    }

    // Notion detection
    if (lowerMessage.includes('notion') ||
        lowerMessage.includes('timeline')) {
        detectedTools.push('notion');
    }

    // GitHub detection
    if (lowerMessage.includes('github') ||
        lowerMessage.includes('repository') ||
        lowerMessage.includes('pull request') ||
        lowerMessage.includes('issue')) {
        detectedTools.push('github');
    }

    // Calendly detection
    if (lowerMessage.includes('calendly') ||
        lowerMessage.includes('scheduled') ||
        lowerMessage.includes('availability') ||
        lowerMessage.includes('calendar')) {
        detectedTools.push('calendly');
    }

    return detectedTools;
}
