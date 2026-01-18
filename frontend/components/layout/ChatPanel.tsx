'use client';

import React, { useState, useCallback } from 'react';
import { AgentFeed } from '../agents/AgentFeed';
import { useAgentStream, AgentUpdate } from '../../hooks/useAgentStream';

/**
 * Props for the ChatPanel component
 */
interface ChatPanelProps {
    /** Whether the chat panel is currently open */
    isOpen: boolean;
    /** Callback to close the chat panel */
    onClose: () => void;
    /** Current event ID for filtering agent updates */
    eventId: string;
}

// API base URL - will be replaced with config value once Next.js is set up
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Chat panel component with input box and agent feed
 * 
 * Features:
 * - Fixed 25% width when open
 * - Collapsible with smooth animation
 * - Input box at bottom
 * - Cursor-style agent feed above input
 * - SSE connection for real-time updates
 * 
 * @example
 * ```tsx
 * <ChatPanel
 *   isOpen={isChatOpen}
 *   onClose={() => setIsChatOpen(false)}
 *   eventId={selectedEventId}
 * />
 * ```
 */
export function ChatPanel({ isOpen, onClose, eventId }: ChatPanelProps): React.ReactElement | null {
    const [message, setMessage] = useState('');
    const [updates, setUpdates] = useState<AgentUpdate[]>([]);
    const [isLoading, setIsLoading] = useState(false);

    // Subscribe to agent updates via SSE
    const handleAgentUpdate = useCallback((update: AgentUpdate) => {
        setUpdates((prev) => [...prev, update]);
    }, []);

    useAgentStream(handleAgentUpdate, {
        enabled: isOpen,
        eventId,
    });

    /**
     * Send message to backend
     */
    const handleSend = async (): Promise<void> => {
        if (!message.trim() || isLoading) {
            return;
        }

        const currentMessage = message;
        setMessage('');
        setIsLoading(true);

        try {
            const response = await fetch(`${API_BASE}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: currentMessage,
                    event_id: eventId,
                }),
            });

            if (!response.ok) {
                throw new Error(`Failed to send message: ${response.statusText}`);
            }

            // Response will come through SSE stream
            console.log('[ChatPanel] Message sent successfully');
        } catch (error) {
            console.error('[ChatPanel] Failed to send message:', error);
            // Add error to feed
            setUpdates((prev) => [
                ...prev,
                {
                    agentName: 'System',
                    status: 'error',
                    message: 'Failed to send message. Please try again.',
                    timestamp: new Date().toISOString(),
                },
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    /**
     * Handle keyboard events for input
     */
    const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>): void => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleSend();
        }
    };

    // Don't render if closed
    if (!isOpen) {
        return null;
    }

    return (
        <div
            className="w-1/4 min-w-[300px] h-full flex flex-col bg-gray-50 border-r border-gray-200"
            role="complementary"
            aria-label="Chat panel"
        >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 bg-white">
                <h2 className="text-lg font-semibold text-gray-900">Nexus Chat</h2>
                <button
                    onClick={onClose}
                    className="p-1 rounded-md hover:bg-gray-100 transition-colors"
                    aria-label="Close chat panel"
                >
                    <svg
                        className="w-5 h-5 text-gray-500"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        aria-hidden="true"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M6 18L18 6M6 6l12 12"
                        />
                    </svg>
                </button>
            </div>

            {/* Agent Feed */}
            <AgentFeed updates={updates} />

            {/* Input Area */}
            <div className="p-4 border-t border-gray-200 bg-white">
                <div className="flex items-center space-x-2">
                    <input
                        type="text"
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask anything about your events..."
                        disabled={isLoading}
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                        aria-label="Chat message input"
                    />
                    <button
                        onClick={handleSend}
                        disabled={isLoading || !message.trim()}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                        aria-label="Send message"
                    >
                        {isLoading ? (
                            <svg
                                className="w-5 h-5 animate-spin"
                                fill="none"
                                viewBox="0 0 24 24"
                                aria-hidden="true"
                            >
                                <circle
                                    className="opacity-25"
                                    cx="12"
                                    cy="12"
                                    r="10"
                                    stroke="currentColor"
                                    strokeWidth="4"
                                />
                                <path
                                    className="opacity-75"
                                    fill="currentColor"
                                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                />
                            </svg>
                        ) : (
                            <svg
                                className="w-5 h-5"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                                aria-hidden="true"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                                />
                            </svg>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ChatPanel;
