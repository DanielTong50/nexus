"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    CheckCircle2,
    Loader2,
    AlertCircle,
    ChevronDown,
    ChevronRight
} from "lucide-react";

export type ToolCall = {
    toolName: string;
    status: "pending" | "success" | "error";
    input?: string;
    output?: string;
};

export type Message = {
    id: string;
    role: "user" | "assistant" | "system";
    agentName?: string;
    content: string;
    isStreaming?: boolean;
    toolCalls?: ToolCall[];
};

interface AgentMessageProps {
    message: Message;
}

export function AgentMessage({ message }: AgentMessageProps) {
    const isUser = message.role === "user";

    if (isUser) {
        return (
            <div className="mb-6">
                <div className="text-xs text-slate-400 mb-1">You</div>
                <div className="text-sm text-slate-900 leading-relaxed">
                    {message.content}
                </div>
            </div>
        );
    }

    return (
        <div className="mb-6">
            {/* Agent Label */}
            <div className="flex items-center gap-2 mb-2">
                <div className="h-5 w-5 rounded bg-slate-900 flex items-center justify-center">
                    <span className="text-[10px] text-white font-medium">N</span>
                </div>
                <span className="text-xs text-slate-500">
                    {message.agentName || "Nexus"}
                </span>
            </div>

            {/* Tool Calls */}
            {message.toolCalls && message.toolCalls.length > 0 && (
                <div className="space-y-2 mb-3">
                    {message.toolCalls.map((tool, idx) => (
                        <ToolCallCard key={idx} tool={tool} />
                    ))}
                </div>
            )}

            {/* Content */}
            <div className="text-sm text-slate-700 leading-relaxed pl-7">
                {message.content}
                {message.isStreaming && (
                    <span className="inline-block w-1 h-4 ml-0.5 bg-slate-400 animate-pulse" />
                )}
            </div>
        </div>
    );
}

function ToolCallCard({ tool }: { tool: ToolCall }) {
    const [isExpanded, setIsExpanded] = useState(false);
    const isPending = tool.status === "pending";
    const isSuccess = tool.status === "success";

    return (
        <div className="ml-7 rounded border border-slate-200 bg-slate-50 text-xs overflow-hidden">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full flex items-center gap-2 px-3 py-2 hover:bg-slate-100 transition-colors text-left"
            >
                {isPending ? (
                    <Loader2 className="h-3 w-3 text-slate-400 animate-spin" />
                ) : isSuccess ? (
                    <CheckCircle2 className="h-3 w-3 text-emerald-500" />
                ) : (
                    <AlertCircle className="h-3 w-3 text-red-500" />
                )}

                <code className="font-mono text-slate-600">{tool.toolName}</code>

                {tool.input && (
                    <span className="text-slate-400 truncate max-w-[150px]">
                        ({tool.input})
                    </span>
                )}

                <div className="ml-auto">
                    {isExpanded ? (
                        <ChevronDown className="h-3 w-3 text-slate-400" />
                    ) : (
                        <ChevronRight className="h-3 w-3 text-slate-400" />
                    )}
                </div>
            </button>

            <AnimatePresence>
                {isExpanded && tool.output && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.15 }}
                        className="overflow-hidden"
                    >
                        <div className="px-3 py-2 bg-slate-900 font-mono text-slate-300 whitespace-pre-wrap">
                            {tool.output}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
