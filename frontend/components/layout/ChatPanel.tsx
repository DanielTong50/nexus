"use client";

import { cn } from "@/lib/utils";

interface ChatPanelProps {
    isOpen: boolean;
    onClose: () => void;
    eventId: string;
}

/**
 * Chat panel skeleton - to be implemented by Frontend Dev 2.
 * Fixed 25% width when open, with input box at bottom.
 */
export function ChatPanel({ isOpen, onClose, eventId }: ChatPanelProps): React.ReactElement {
    return (
        <aside
            className={cn(
                "w-1/4 min-w-[300px] max-w-[400px] h-screen",
                "bg-slate-800 text-secondary",
                "flex flex-col",
                "border-l border-slate-700",
                "transition-transform duration-300",
                isOpen ? "translate-x-0" : "-translate-x-full"
            )}
            role="complementary"
            aria-label="Chat panel"
        >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-slate-700">
                <h2 className="text-lg font-semibold text-white">Chat</h2>
                <button
                    onClick={onClose}
                    className="p-1 rounded hover:bg-slate-700 transition-colors"
                    aria-label="Close chat panel"
                >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>

            {/* Agent Feed Area - Skeleton placeholder */}
            <div className="flex-1 overflow-auto p-4">
                <div className="text-center text-slate-400 py-8">
                    <p className="text-sm">Agent feed will appear here</p>
                    <p className="text-xs mt-2 text-slate-500">
                        (To be implemented by Frontend Dev 2)
                    </p>
                    {eventId && (
                        <p className="text-xs mt-2 text-slate-500">
                            Event ID: {eventId}
                        </p>
                    )}
                </div>
            </div>

            {/* Input Box - Skeleton placeholder */}
            <div className="p-4 border-t border-slate-700">
                <div className="flex gap-2">
                    <input
                        type="text"
                        placeholder="Type a message..."
                        className={cn(
                            "flex-1 px-4 py-2 rounded-lg",
                            "bg-slate-700 text-white placeholder-slate-400",
                            "border border-slate-600",
                            "focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
                        )}
                        disabled
                    />
                    <button
                        className={cn(
                            "px-4 py-2 rounded-lg",
                            "bg-accent text-white",
                            "hover:bg-blue-600 transition-colors",
                            "disabled:opacity-50 disabled:cursor-not-allowed"
                        )}
                        disabled
                    >
                        Send
                    </button>
                </div>
            </div>
        </aside>
    );
}
