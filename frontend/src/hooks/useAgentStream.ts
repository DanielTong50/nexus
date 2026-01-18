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
    EditedFile
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

    // Track current agent task being built
    const currentTaskRef = useRef<AgentTask | null>(null);
    const stepCounterRef = useRef(0);
    const idCounter = useRef(0);

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

            case "agent_start": {
                // Create a new agent task
                const agentName = agent_name || 'Agent';
                stepCounterRef.current = 0;

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

                currentTaskRef.current = agentTask;
                setFeedItems(prev => [...prev, { type: 'agent', data: agentTask }]);
                break;
            }

            case "tool_call":
            case "agent_tool_call":
            case "tool_use":
            case "function_call": {
                if (!currentTaskRef.current) break;

                // Handle different possible field names for tool name
                const toolName = (data.tool_name || data.name || data.function || data.tool) as string;
                const status = data.status as 'pending' | 'success' | 'error';
                const currentId = currentTaskRef.current.id;

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
                if (!currentTaskRef.current) break;

                const chunk = data.content as string;
                const currentId = currentTaskRef.current.id;

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
                if (!currentTaskRef.current) break;

                const currentId = currentTaskRef.current.id;
                const completeMessage = data.message as string;

                setFeedItems(prev => {
                    const updated = [...prev];
                    const taskItem = updated.find(
                        item => item.type === 'agent' && item.data.id === currentId
                    );

                    if (taskItem?.type === 'agent') {
                        taskItem.data.status = 'complete';
                        taskItem.data.statusMessage = 'Task complete';
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

            default:
                console.log("Unknown event type:", event_type, data);
        }
    }, [generateId]);

    const sendMessage = useCallback(async (userMessage: string) => {
        if (!userMessage.trim()) return;

        setError(null);
        setIsStreaming(true);
        currentTaskRef.current = null;
        stepCounterRef.current = 0;

        // Add user message immediately
        const userMsg: UserMessage = {
            id: generateId(),
            content: userMessage,
            timestamp: new Date().toISOString(),
        };
        setFeedItems(prev => [...prev, { type: 'user', data: userMsg }]);

        try {
            const response = await fetch(ENDPOINTS.chatStream, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    message: userMessage,
                    request_id: `req-${Date.now()}`,
                }),
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
        stepCounterRef.current = 0;
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
