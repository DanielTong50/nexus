'use client';

import { useEffect, useCallback } from 'react';

/**
 * Status of an agent during execution
 */
export type AgentStatus = 'thinking' | 'executing' | 'complete' | 'error';

/**
 * Update received from an agent via SSE
 */
export interface AgentUpdate {
    /** Name of the agent (e.g., "Partnerships", "Finance") */
    agentName: string;
    /** Current execution status */
    status: AgentStatus;
    /** Human-readable message about current action */
    message: string;
    /** Optional link to document (Google Sheet, Slack, etc.) */
    documentLink?: string;
    /** Timestamp of the update */
    timestamp?: string;
}

/**
 * Configuration options for the SSE connection
 */
interface UseAgentStreamOptions {
    /** Whether the stream should be active */
    enabled?: boolean;
    /** Event ID to filter updates for */
    eventId?: string;
}

// API base URL - will be replaced with config value once Next.js is set up
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Hook to connect to the backend SSE stream and receive agent updates
 * 
 * @param onUpdate - Callback fired when a new agent update is received
 * @param options - Configuration options for the stream
 * 
 * @example
 * ```tsx
 * const [updates, setUpdates] = useState<AgentUpdate[]>([]);
 * 
 * useAgentStream((update) => {
 *   setUpdates(prev => [...prev, update]);
 * }, { enabled: isChatOpen });
 * ```
 */
export function useAgentStream(
    onUpdate: (update: AgentUpdate) => void,
    options: UseAgentStreamOptions = {}
): void {
    const { enabled = true, eventId } = options;

    const handleMessage = useCallback(
        (event: MessageEvent) => {
            try {
                const update: AgentUpdate = JSON.parse(event.data);
                onUpdate(update);
            } catch (error) {
                console.error('[useAgentStream] Failed to parse SSE message:', error);
            }
        },
        [onUpdate]
    );

    useEffect(() => {
        if (!enabled) {
            return;
        }

        // Build SSE endpoint URL
        const url = new URL(`${API_BASE}/api/chat/stream`);
        if (eventId) {
            url.searchParams.set('event_id', eventId);
        }

        // Create EventSource connection
        const eventSource = new EventSource(url.toString());

        eventSource.onopen = () => {
            console.log('[useAgentStream] SSE connection opened');
        };

        eventSource.onmessage = handleMessage;

        eventSource.onerror = (error) => {
            console.error('[useAgentStream] SSE connection error:', error);
            // EventSource will automatically attempt to reconnect
        };

        // Cleanup on unmount or when dependencies change
        return () => {
            console.log('[useAgentStream] Closing SSE connection');
            eventSource.close();
        };
    }, [enabled, eventId, handleMessage]);
}

export default useAgentStream;
