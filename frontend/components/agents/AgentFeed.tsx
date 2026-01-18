"use client";

interface AgentUpdate {
    agentName: string;
    status: 'thinking' | 'executing' | 'complete' | 'error';
    message: string;
    documentLink?: string;
}

interface AgentFeedProps {
    updates: AgentUpdate[];
}

/**
 * Cursor-style agent feed component.
 * Shows streaming updates from agents with clickable document links.
 * 
 * Skeleton to be implemented by Frontend Dev 2.
 */
export function AgentFeed({ updates }: AgentFeedProps): React.ReactElement {
    return (
        <div className="space-y-3">
            {updates.length === 0 ? (
                <p className="text-sm text-slate-400 text-center py-4">
                    Agent updates will appear here
                </p>
            ) : (
                updates.map((update, index) => (
                    <div
                        key={index}
                        className="p-3 rounded-lg bg-slate-700/50 text-sm"
                    >
                        <div className="flex items-center gap-2 mb-1">
                            <span className="font-medium text-white">{update.agentName}</span>
                            <span className={`text-xs px-2 py-0.5 rounded ${update.status === 'thinking' ? 'bg-yellow-500/20 text-yellow-400' :
                                    update.status === 'executing' ? 'bg-blue-500/20 text-blue-400' :
                                        update.status === 'complete' ? 'bg-green-500/20 text-green-400' :
                                            'bg-red-500/20 text-red-400'
                                }`}>
                                {update.status}
                            </span>
                        </div>
                        <p className="text-slate-300">{update.message}</p>
                        {update.documentLink && (
                            <a
                                href={update.documentLink}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-accent hover:underline text-xs mt-1 inline-block"
                            >
                                📄 Open document →
                            </a>
                        )}
                    </div>
                ))
            )}
        </div>
    );
}
