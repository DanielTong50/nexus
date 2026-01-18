"use client";

import { useState, useRef, useEffect } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Sparkles, Loader2, AlertCircle, Trash2 } from "lucide-react";
import { useAgentStream } from "@/hooks/useAgentStream";
import { AgentMessage } from "@/components/agents/AgentMessage";

export function ChatPanel() {
    const [inputValue, setInputValue] = useState("");
    const { messages, isStreaming, error, sendMessage, clearMessages } = useAgentStream();
    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when messages change
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSubmit = async (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!inputValue.trim() || isStreaming) return;

        const message = inputValue;
        setInputValue("");
        await sendMessage(message);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <header className="h-14 px-4 flex items-center justify-between border-b border-gray-200 flex-shrink-0">
                <div className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-gray-400" />
                    <span className="text-sm font-medium text-gray-900">Agent Intelligence</span>
                </div>
                <div className="flex items-center gap-3">
                    {error && (
                        <div className="flex items-center gap-1 text-red-500">
                            <AlertCircle className="h-3 w-3" />
                            <span className="text-xs">Error</span>
                        </div>
                    )}
                    <div className="flex items-center gap-1.5">
                        <div className={`h-2 w-2 rounded-full ${isStreaming ? 'bg-amber-500' : 'bg-green-500'}`} />
                        <span className="text-xs text-gray-500">
                            {isStreaming ? "Processing" : "Active"}
                        </span>
                    </div>
                    {messages.length > 0 && (
                        <button
                            onClick={clearMessages}
                            className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors"
                            title="Clear chat"
                        >
                            <Trash2 className="h-3.5 w-3.5" />
                        </button>
                    )}
                </div>
            </header>

            {/* Messages Feed */}
            <ScrollArea className="flex-1" ref={scrollRef}>
                <div className="p-4">
                    {messages.length === 0 ? (
                        <div className="text-center py-12">
                            <Sparkles className="h-8 w-8 mx-auto mb-3 text-gray-300" />
                            <p className="text-sm text-gray-500">Ask the agent anything about your event.</p>
                            <p className="text-xs text-gray-400 mt-1">Try: &quot;Check sponsor status for Google&quot;</p>
                        </div>
                    ) : (
                        <div className="space-y-1">
                            {messages.map((msg) => (
                                <AgentMessage key={msg.id} message={msg} />
                            ))}
                            {isStreaming && (
                                <div className="flex items-center gap-2 text-gray-400 text-xs py-2">
                                    <Loader2 className="h-3 w-3 animate-spin" />
                                    <span>Agent is thinking...</span>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </ScrollArea>

            {/* Input Area */}
            <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
                <div className="rounded-lg border border-gray-200 bg-white focus-within:border-gray-300 transition-colors">
                    <textarea
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask the agent anything..."
                        rows={2}
                        disabled={isStreaming}
                        className="w-full p-3 text-sm resize-none outline-none bg-transparent placeholder:text-gray-400 disabled:opacity-50"
                    />
                    <div className="flex justify-end px-3 pb-3">
                        <button
                            type="submit"
                            disabled={!inputValue.trim() || isStreaming}
                            className="flex items-center gap-2 px-4 py-1.5 text-xs font-medium text-white bg-gray-900 hover:bg-gray-800 rounded-md disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            {isStreaming ? (
                                <>
                                    <Loader2 className="h-3 w-3 animate-spin" />
                                    Processing
                                </>
                            ) : (
                                "Run Agent"
                            )}
                        </button>
                    </div>
                </div>
            </form>
        </div>
    );
}
