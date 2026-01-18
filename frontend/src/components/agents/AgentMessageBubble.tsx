"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Terminal } from "lucide-react";
import { TypewriterEffect } from "@/components/ui/TypewriterEffect";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { cn } from "@/lib/utils";

export interface ToolCall {
    id: string;
    toolName: string;
    count: number;
    status: "running" | "success" | "error";
    input: string; // JSON string
    output?: string; // JSON string
}

export interface AgentMessageProps {
    agentName: string;
    content: string;
    timestamp: string;
    toolCalls?: ToolCall[];
    isThinking?: boolean;
}

export function AgentMessageBubble({
    agentName,
    content,
    timestamp,
    toolCalls = [],
    isThinking = false,
}: AgentMessageProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            className="flex flex-col gap-2 p-4 rounded-lg border bg-card/50 shadow-sm"
        >
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className={cn(
                        "w-2 h-2 rounded-full",
                        isThinking ? "bg-blue-500 animate-pulse" : "bg-green-500"
                    )} />
                    <span className="font-semibold text-sm">{agentName}</span>
                </div>
                <span className="text-xs text-muted-foreground">{timestamp}</span>
            </div>

            {/* Main Content */}
            <div className="text-sm leading-relaxed text-foreground/90 font-mono">
                <TypewriterEffect text={content} speed={10} />
            </div>

            {/* Tool Calls Section */}
            {toolCalls.length > 0 && (
                <div className="mt-3 space-y-2">
                    {toolCalls.map((tool) => (
                        <ToolCallCard key={tool.id} tool={tool} />
                    ))}
                </div>
            )}
        </motion.div>
    );
}

function ToolCallCard({ tool }: { tool: ToolCall }) {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <motion.div
            layout
            className="border rounded-md overflow-hidden bg-background text-xs"
        >
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="w-full flex items-center justify-between p-2 hover:bg-muted/50 transition-colors"
            >
                <div className="flex items-center gap-2">
                    <StatusBadge status={tool.status} />
                    <span className="font-medium text-muted-foreground flex items-center gap-1">
                        <Terminal className="w-3 h-3" />
                        {tool.toolName}
                    </span>
                </div>
                <motion.div
                    animate={{ rotate: isOpen ? 180 : 0 }}
                    transition={{ duration: 0.2 }}
                >
                    <ChevronDown className="w-3 h-3 text-muted-foreground" />
                </motion.div>
            </button>

            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="border-t bg-muted/20"
                    >
                        <div className="p-2 space-y-2 font-mono overflow-x-auto">
                            <div>
                                <div className="text-muted-foreground text-[10px] uppercase mb-1">Input</div>
                                <pre className="text-xs text-blue-400">{tool.input}</pre>
                            </div>
                            {tool.output && (
                                <div>
                                    <div className="text-muted-foreground text-[10px] uppercase mb-1">Output</div>
                                    <pre className="text-xs text-green-400">{tool.output}</pre>
                                </div>
                            )}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
}
