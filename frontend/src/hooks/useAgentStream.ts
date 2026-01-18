"use client";

/**
 * useAgentStream hook - SSE streaming connection to backend
 * 
 * Connects to the FastAPI backend's /api/chat/stream endpoint
 * and parses Server-Sent Events into Message objects for the UI.
 */

import { useState, useCallback, useRef } from "react";
import { ENDPOINTS } from "@/lib/config";
import { Message, ToolCall } from "@/components/agents/AgentMessage";

// Backend event types
interface BackendStreamEvent {
    event_type: string;
    data: Record<string, unknown>;
    agent_name?: string;
    timestamp: string;
}

export interface UseAgentStreamReturn {
    messages: Message[];
    isStreaming: boolean;
    error: string | null;
    sendMessage: (message: string) => Promise<void>;
    clearMessages: () => void;
}

export function useAgentStream(): UseAgentStreamReturn {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isStreaming, setIsStreaming] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Track current streaming message for appending chunks
    const currentMessageRef = useRef<Message | null>(null);
    const messageIdCounter = useRef(0);

    const generateId = useCallback(() => {
        messageIdCounter.current += 1;
        return `msg-${Date.now()}-${messageIdCounter.current}`;
    }, []);

    // Process SSE events - defined inline to avoid dependency issues
    const processEvent = useCallback((event: BackendStreamEvent) => {
        const { event_type, data, agent_name } = event;

        switch (event_type) {
            case "classification":
                // Show classification status
                setMessages((prev) => [
                    ...prev,
                    {
                        id: generateId(),
                        role: "assistant",
                        agentName: "Router",
                        content: data.message as string,
                        isStreaming: true,
                    },
                ]);
                break;

            case "routing":
                // Update router message with routing info
                setMessages((prev) => {
                    const updated = [...prev];
                    const lastMsg = updated[updated.length - 1];
                    if (lastMsg && lastMsg.agentName === "Router") {
                        lastMsg.content = data.message as string;
                        lastMsg.isStreaming = false;
                    }
                    return updated;
                });
                break;

            case "agent_start": {
                // Create a new message for the agent
                const agentMsg: Message = {
                    id: generateId(),
                    role: "assistant",
                    agentName: agent_name || "Agent",
                    content: "",
                    isStreaming: true,
                    toolCalls: [],
                };
                currentMessageRef.current = agentMsg;
                setMessages((prev) => [...prev, agentMsg]);
                break;
            }

            case "tool_call":
            case "agent_tool_call": {
                // Add or update tool call in current message
                if (currentMessageRef.current) {
                    const toolCall: ToolCall = {
                        toolName: data.tool_name as string,
                        status: data.status as "pending" | "success" | "error",
                        input: typeof data.input === "object" ? JSON.stringify(data.input) : data.input as string,
                        output: data.output ? JSON.stringify(data.output, null, 2) : undefined,
                    };

                    setMessages((prev) => {
                        const updated = [...prev];
                        const current = updated.find((m) => m.id === currentMessageRef.current?.id);
                        if (current) {
                            // Update existing tool call or add new one
                            const existingIdx = current.toolCalls?.findIndex(
                                (tc) => tc.toolName === toolCall.toolName
                            );
                            if (existingIdx !== undefined && existingIdx >= 0 && current.toolCalls) {
                                current.toolCalls[existingIdx] = toolCall;
                            } else {
                                current.toolCalls = [...(current.toolCalls || []), toolCall];
                            }
                        }
                        return updated;
                    });
                }
                break;
            }

            case "text_chunk":
            case "agent_update":
                // Append text chunk to current message
                if (currentMessageRef.current) {
                    const chunk = data.content as string;
                    const currentId = currentMessageRef.current.id;
                    setMessages((prev) =>
                        prev.map((m) =>
                            m.id === currentId
                                ? { ...m, content: m.content + chunk }
                                : m
                        )
                    );
                }
                break;

            case "agent_complete":
                // Mark agent message as complete
                if (currentMessageRef.current) {
                    const currentId = currentMessageRef.current.id;
                    const completeMessage = data.message as string;
                    setMessages((prev) =>
                        prev.map((m) =>
                            m.id === currentId
                                ? {
                                    ...m,
                                    isStreaming: false,
                                    content: m.content || completeMessage || "",
                                }
                                : m
                        )
                    );
                }
                break;

            case "complete":
                // Stream finished
                setIsStreaming(false);
                break;

            case "error":
                setError(data.error as string);
                setMessages((prev) => [
                    ...prev,
                    {
                        id: generateId(),
                        role: "assistant",
                        agentName: "System",
                        content: `Error: ${data.error}`,
                    },
                ]);
                break;

            default:
                console.log("Unknown event type:", event_type, data);
        }
    }, [generateId]);

    const sendMessage = useCallback(async (userMessage: string) => {
        if (!userMessage.trim()) return;

        setError(null);
        setIsStreaming(true);
        currentMessageRef.current = null;

        // Add user message immediately
        const userMsg: Message = {
            id: generateId(),
            role: "user",
            content: userMessage,
        };
        setMessages((prev) => [...prev, userMsg]);

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

                // Process complete SSE messages (lines ending with \n\n)
                const lines = buffer.split("\n");
                buffer = lines.pop() || ""; // Keep incomplete line in buffer

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

            // Add error message
            setMessages((prev) => [
                ...prev,
                {
                    id: generateId(),
                    role: "assistant",
                    agentName: "System",
                    content: `Error: ${errorMessage}. Please check if the backend is running at ${ENDPOINTS.chatStream}`,
                },
            ]);
        } finally {
            setIsStreaming(false);
            currentMessageRef.current = null;
        }
    }, [generateId, processEvent]);

    const clearMessages = useCallback(() => {
        setMessages([]);
        setError(null);
        currentMessageRef.current = null;
    }, []);

    return {
        messages,
        isStreaming,
        error,
        sendMessage,
        clearMessages,
    };
}
