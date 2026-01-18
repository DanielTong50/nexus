"use client";

import { useState, ReactNode } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface ThinkingDropdownProps {
    thinkingTime: string;      // e.g., "7s"
    content?: string;          // The actual thinking/reasoning text
    defaultExpanded?: boolean;
    agentName?: string;        // Optional - kept for backwards compatibility
    agentIcon?: ReactNode;     // Optional - kept for backwards compatibility
}

export function ThinkingDropdown({
    thinkingTime,
    content,
    defaultExpanded = false,
}: ThinkingDropdownProps) {
    const [isExpanded, setIsExpanded] = useState(defaultExpanded);
    const hasContent = Boolean(content);

    return (
        <div className="relative">
            <button
                onClick={() => hasContent && setIsExpanded(!isExpanded)}
                disabled={!hasContent}
                className={cn(
                    "flex items-center gap-1.5",
                    "text-sm text-slate-500",
                    "transition-colors duration-150",
                    hasContent && "hover:text-slate-700 cursor-pointer"
                )}
            >
                {hasContent && (
                    <motion.div
                        animate={{ rotate: isExpanded ? 90 : 0 }}
                        transition={{ duration: 0.15 }}
                    >
                        <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
                    </motion.div>
                )}

                <span className="text-slate-500">
                    Thought for <span className="font-medium text-slate-600">{thinkingTime}</span>
                </span>
            </button>

            <AnimatePresence>
                {isExpanded && content && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                        className="absolute left-0 bottom-full mb-2 w-80 z-10 overflow-hidden"
                    >
                        <div className="p-3 rounded-md bg-white border border-slate-200 shadow-lg">
                            <pre className="text-xs text-slate-600 whitespace-pre-wrap font-mono leading-relaxed max-h-48 overflow-y-auto">
                                {content}
                            </pre>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
