"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Sparkles, Loader2, AlertCircle, Trash2 } from "lucide-react";
import { useAgentStream } from "@/hooks/useAgentStream";
import { AgentMessage } from "@/components/agents/AgentMessage";

export function ChatPanel() {
    const [inputValue, setInputValue] = useState("");
    const { messages, isStreaming, error, sendMessage, clearMessages } = useAgentStream();
    const scrollRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLTextAreaElement>(null);

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
            <header className="h-14 px-5 flex items-center justify-between border-b border-slate-200 flex-shrink-0">
                <div className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-slate-400" />
                    <span className="text-sm font-medium text-slate-900">Agent Intelligence</span>
                </div>
                <div className="flex items-center gap-3">
                    {error && (
                        <div className="flex items-center gap-1 text-red-500">
                            <AlertCircle className="h-3 w-3" />
                            <span className="text-xs">Error</span>
                        </div>
                    )}
                    <div className="flex items-center gap-1">
                        <div className={`h-2 w-2 rounded-full ${isStreaming ? 'bg-amber-500 animate-pulse' : 'bg-emerald-500'}`} />
                        <span className="text-xs text-slate-500">
                            {isStreaming ? "Processing..." : "Active"}
                        </span>
                    </div>
                    {messages.length > 0 && (
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={clearMessages}
                            className="h-7 w-7 p-0 text-slate-400 hover:text-slate-600"
                            title="Clear chat"
                        >
                            <Trash2 className="h-3 w-3" />
                        </Button>
                    )}
                </div>
            </header>

            {/* Messages Feed */}
            <ScrollArea className="flex-1" ref={scrollRef}>
                <div className="p-5">
                    {messages.length === 0 ? (
                        <div className="text-center text-slate-400 text-sm py-10">
                            <Sparkles className="h-8 w-8 mx-auto mb-3 opacity-50" />
                            <p>Ask the agent anything about your event.</p>
                            <p className="text-xs mt-1">Try: &quot;Check sponsor status for Google&quot;</p>
                        </div>
                    ) : (
                        <div className="space-y-1">
                            {messages.map((msg) => (
                                <AgentMessage key={msg.id} message={msg} />
                            ))}
                            {isStreaming && (
                                <div className="flex items-center gap-2 text-slate-400 text-xs py-2">
                                    <Loader2 className="h-3 w-3 animate-spin" />
                                    <span>Agent is thinking...</span>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </ScrollArea>

            <Separator />

            {/* Input Area */}
            <form onSubmit={handleSubmit} className="p-4 bg-white">
                <div className="rounded-lg border border-slate-200 bg-white focus-within:border-slate-300 transition-colors">
                    <textarea
                        ref={inputRef}
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Ask the agent anything..."
                        rows={2}
                        disabled={isStreaming}
                        className="w-full p-3 text-sm resize-none outline-none bg-transparent placeholder:text-slate-400 disabled:opacity-50"
                    />
                    <div className="flex justify-end px-3 pb-3">
                        <Button
                            type="submit"
                            size="sm"
                            disabled={!inputValue.trim() || isStreaming}
                            className="bg-slate-900 hover:bg-slate-800 text-white h-8 px-4 text-xs disabled:opacity-50"
                        >
                            {isStreaming ? (
                                <>
                                    <Loader2 className="h-3 w-3 mr-2 animate-spin" />
                                    Processing
                                </>
                            ) : (
                                "Run Agent"
                            )}
                        </Button>
                    </div>
                </div>
            </form>
        </div>
    );
}
