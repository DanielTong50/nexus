'use client';

import React from 'react';
import { AgentUpdate, AgentStatus } from '../../hooks/useAgentStream';

/**
 * Props for the AgentFeed component
 */
interface AgentFeedProps {
    /** Array of agent updates to display */
    updates: AgentUpdate[];
}

/**
 * Get styling classes for status badge based on agent status
 */
function getStatusStyles(status: AgentStatus): string {
    switch (status) {
        case 'thinking':
            return 'bg-blue-100 text-blue-800';
        case 'executing':
            return 'bg-yellow-100 text-yellow-800';
        case 'complete':
            return 'bg-green-100 text-green-800';
        case 'error':
            return 'bg-red-100 text-red-800';
        default:
            return 'bg-gray-100 text-gray-800';
    }
}

/**
 * Get display text for status badge
 */
function getStatusText(status: AgentStatus): string {
    switch (status) {
        case 'thinking':
            return '● Thinking...';
        case 'executing':
            return '● Executing...';
        case 'complete':
            return '✓ Complete';
        case 'error':
            return '✗ Error';
        default:
            return status;
    }
}

/**
 * Cursor-style agent feed component
 * 
 * Displays real-time updates from agents including:
 * - Agent name and status
 * - Current action/message
 * - Clickable document links
 * 
 * @example
 * ```tsx
 * const [updates, setUpdates] = useState<AgentUpdate[]>([]);
 * <AgentFeed updates={updates} />
 * ```
 */
export function AgentFeed({ updates }: AgentFeedProps): React.ReactElement {
    const feedRef = React.useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when new updates arrive
    React.useEffect(() => {
        if (feedRef.current) {
            feedRef.current.scrollTop = feedRef.current.scrollHeight;
        }
    }, [updates]);

    if (updates.length === 0) {
        return (
            <div className="flex-1 flex items-center justify-center text-gray-400 text-sm">
                <p>Send a message to start...</p>
            </div>
        );
    }

    return (
        <div
            ref={feedRef}
            className="flex-1 overflow-y-auto space-y-3 p-4"
            role="log"
            aria-live="polite"
            aria-label="Agent activity feed"
        >
            {updates.map((update, index) => (
                <div
                    key={`${update.agentName}-${update.timestamp || index}`}
                    className="bg-white border border-gray-200 rounded-lg p-3 shadow-sm"
                >
                    {/* Header: Agent name and status */}
                    <div className="flex items-center justify-between mb-2">
                        <span className="font-semibold text-gray-900">
                            {update.agentName}
                        </span>
                        <span
                            className={`text-xs px-2 py-1 rounded-full font-medium ${getStatusStyles(update.status)}`}
                        >
                            {getStatusText(update.status)}
                        </span>
                    </div>

                    {/* Message */}
                    <p className="text-sm text-gray-700">{update.message}</p>

                    {/* Document link if present */}
                    {update.documentLink && (
                        <a
                            href={update.documentLink}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center mt-2 text-sm text-blue-600 hover:text-blue-800 hover:underline"
                        >
                            <svg
                                className="w-4 h-4 mr-1"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                                aria-hidden="true"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                                />
                            </svg>
                            Open Document
                        </a>
                    )}
                </div>
            ))}
        </div>
    );
}

export default AgentFeed;
