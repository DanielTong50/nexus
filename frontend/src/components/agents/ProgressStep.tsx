"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Check, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { ToolIcon, getToolDisplayName } from "./ToolIcon";
import type { ProgressStep as ProgressStepType } from "./types";

interface ProgressStepProps {
    step: ProgressStepType;
    isLast?: boolean;
}

export function ProgressStep({ step, isLast = false }: ProgressStepProps) {
    const [isExpanded, setIsExpanded] = useState(false);
    const hasExpandedContent = Boolean(step.expandedContent);

    const isPending = step.status === 'pending';
    const isRunning = step.status === 'running';
    const isComplete = step.status === 'complete';

    // Extract tool name from description for icon lookup
    const toolName = step.description.toLowerCase().replace(/\s+/g, '_');
    const displayName = getToolDisplayName(step.description);

    return (
        <div className={cn("relative", !isLast && "pb-2")}>
            <div className="flex items-center gap-2">
                {/* Status indicator */}
                <div className="relative flex-shrink-0">
                    {isComplete ? (
                        <Check className="w-4 h-4 text-emerald-500" />
                    ) : isRunning ? (
                        <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
                    ) : (
                        <div className="w-4 h-4 rounded-full border border-slate-300" />
                    )}
                </div>

                {/* Tool icon */}
                <ToolIcon toolName={toolName} size={14} />

                {/* Step content */}
                <button
                    onClick={() => hasExpandedContent && setIsExpanded(!isExpanded)}
                    disabled={!hasExpandedContent}
                    className={cn(
                        "flex items-center gap-1 text-left",
                        hasExpandedContent && "cursor-pointer hover:text-slate-900"
                    )}
                >
                    <span
                        className={cn(
                            "text-sm",
                            isPending && "text-slate-400",
                            isRunning && "text-slate-700",
                            isComplete && "text-slate-600"
                        )}
                    >
                        {displayName}
                    </span>

                    {hasExpandedContent && (
                        <motion.div
                            animate={{ rotate: isExpanded ? 180 : 0 }}
                            transition={{ duration: 0.2 }}
                            className="flex-shrink-0"
                        >
                            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                        </motion.div>
                    )}
                </button>
            </div>

            {/* Expanded content */}
            <AnimatePresence>
                {isExpanded && step.expandedContent && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.15 }}
                        className="overflow-hidden ml-6"
                    >
                        <div className="mt-2 p-2 rounded bg-slate-50">
                            <pre className="text-xs text-slate-600 whitespace-pre-wrap font-mono">
                                {step.expandedContent}
                            </pre>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
