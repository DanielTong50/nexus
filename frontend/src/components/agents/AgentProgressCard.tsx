"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
    ChevronDown,
    ChevronRight,
    Eye,
    Handshake,
    Megaphone,
    DollarSign,
    Calendar,
    Code,
    Sparkles,
    Bot
} from "lucide-react";
import { cn } from "@/lib/utils";
import { ThinkingDropdown } from "./ThinkingDropdown";
import { FilesEditedBadge } from "./FilesEditedBadge";
import { ProgressStep } from "./ProgressStep";
import { ToolIcon, getToolDisplayName } from "./ToolIcon";
import type { AgentTask, AgentTaskStatus } from "./types";
import { AGENT_ICON_NAMES } from "./types";
import { AgentId } from "@/lib/config";

interface AgentProgressCardProps {
    task: AgentTask;
    showReviewButton?: boolean;
    onReviewClick?: () => void;
    defaultExpanded?: boolean;
}

// Icon component mapping
const ICON_COMPONENTS: Record<string, React.FC<{ className?: string }>> = {
    Handshake,
    Megaphone,
    DollarSign,
    Calendar,
    Code,
    Sparkles,
    Bot,
};

// Get icon component for agent
function getAgentIcon(agentId: AgentId, agentName: string) {
    // Special case for Router/System
    if (agentName === 'Router' || agentName === 'System') {
        return ICON_COMPONENTS['Sparkles'];
    }
    const iconName = AGENT_ICON_NAMES[agentId];
    return ICON_COMPONENTS[iconName] || ICON_COMPONENTS['Bot'];
}

// Status colors for the indicator dot
const STATUS_COLORS: Record<AgentTaskStatus, string> = {
    thinking: "bg-amber-500",
    executing: "bg-blue-500",
    analyzing: "bg-violet-500",
    complete: "bg-emerald-500",
    error: "bg-red-500",
};


// Status indicator with optional animation
function StatusIndicator({ status }: { status: AgentTaskStatus }) {
    const isActive = status !== 'complete' && status !== 'error';

    return (
        <div className="relative flex-shrink-0">
            <div className={cn(
                "w-2 h-2 rounded-full",
                STATUS_COLORS[status]
            )} />
            {isActive && (
                <motion.div
                    className={cn(
                        "absolute inset-0 rounded-full",
                        STATUS_COLORS[status]
                    )}
                    animate={{ scale: [1, 1.8, 1.8], opacity: [0.5, 0, 0] }}
                    transition={{ repeat: Infinity, duration: 1.5 }}
                />
            )}
        </div>
    );
}

export function AgentProgressCard({
    task,
    showReviewButton = true,
    onReviewClick,
    defaultExpanded = false
}: AgentProgressCardProps) {
    const [isExpanded, setIsExpanded] = useState(defaultExpanded);

    const IconComponent = getAgentIcon(task.agentId, task.agentName);

    // Compact inline view (collapsed)
    if (!isExpanded) {
        return (
            <motion.button
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                onClick={() => setIsExpanded(true)}
                className={cn(
                    "w-full flex items-center gap-3 px-3 py-2",
                    "rounded-md",
                    "hover:bg-slate-100",
                    "transition-all duration-150",
                    "text-left group"
                )}
            >
                {/* Expand chevron */}
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-slate-600 transition-colors" />

                {/* Agent icon */}
                <IconComponent className="w-4 h-4 text-slate-500 flex-shrink-0" />

                {/* Agent name */}
                <span className="text-sm font-medium text-slate-900">
                    {task.agentName}
                </span>

                {/* Status indicator */}
                <StatusIndicator status={task.status} />

                {/* Status message on same line */}
                {task.statusMessage && (
                    <span className="text-sm text-slate-400 truncate flex-1">
                        {task.statusMessage}
                    </span>
                )}
            </motion.button>
        );
    }

    // Expanded full view
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            className="rounded-md overflow-hidden"
        >


            {/* Main Content */}
            <div className="p-3 space-y-3">
                {/* Agent Header - clickable to collapse */}
                <button
                    onClick={() => setIsExpanded(false)}
                    className="w-full flex items-center gap-2 text-left group"
                >
                    {/* Collapse chevron */}
                    <ChevronDown className="w-4 h-4 text-slate-400 group-hover:text-slate-600 transition-colors flex-shrink-0" />

                    {/* Agent Icon */}
                    <IconComponent className="w-4 h-4 text-slate-500 flex-shrink-0" />

                    {/* Agent Name */}
                    <span className="text-sm font-semibold text-slate-900">
                        {task.agentName}
                    </span>

                    {/* Status Indicator */}
                    <StatusIndicator status={task.status} />

                    {/* Status Message - inline with agent name */}
                    {task.statusMessage && (
                        <span className="text-sm text-slate-400 truncate flex-1">
                            {task.statusMessage}
                        </span>
                    )}
                </button>

                {/* Files Edited */}
                {task.filesEdited.length > 0 && (
                    <div className="pt-2 pl-7">
                        <FilesEditedBadge files={task.filesEdited} />
                    </div>
                )}

                {/* Progress Updates */}
                {task.progressSteps.length > 0 && (
                    <div className="pt-2 pl-7">
                        <div className="pl-1">
                            {task.progressSteps.map((step, index) => (
                                <ProgressStep
                                    key={step.id}
                                    step={step}
                                    isLast={index === task.progressSteps.length - 1}
                                />
                            ))}
                        </div>
                    </div>
                )}

                {/* Tool Calls Used Section - just icons with labels, no header */}
                {task.toolCalls && task.toolCalls.length > 0 && (
                    <div className="pt-1 pl-7">
                        <div className="flex items-center gap-1.5 flex-wrap">
                            {task.toolCalls.map((toolName, index) => (
                                <div 
                                    key={index}
                                    className="flex items-center gap-1 px-1.5 py-0.5 rounded bg-slate-100"
                                    title={getToolDisplayName(toolName)}
                                >
                                    <ToolIcon toolName={toolName} size={12} />
                                    <span className="text-[11px] text-slate-500">
                                        {getToolDisplayName(toolName)}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Completion Message */}
                {task.completionMessage && task.status === 'complete' && (
                    <div className="pt-3 pl-7 border-t border-slate-100">
                        <div className="prose prose-sm prose-slate max-w-none">
                            <div
                                className="text-sm text-slate-700 leading-relaxed"
                                dangerouslySetInnerHTML={{
                                    __html: formatCompletionMessage(task.completionMessage)
                                }}
                            />
                        </div>
                    </div>
                )}
            </div>

            {/* Footer Actions with Thinking integrated */}
            <div className="px-3 py-2 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    {/* Thinking Time */}
                    {task.thinkingTime && (
                        <ThinkingDropdown
                            thinkingTime={task.thinkingTime}
                            content={task.thinkingContent}
                        />
                    )}
                </div>

                {showReviewButton && task.filesEdited.length > 0 && (
                    <button
                        onClick={onReviewClick}
                        className={cn(
                            "flex items-center gap-1.5 px-3 py-1.5 rounded-md",
                            "text-xs font-medium",
                            "bg-white border border-slate-200",
                            "text-slate-700 hover:bg-slate-100 hover:border-slate-300",
                            "transition-colors duration-150"
                        )}
                    >
                        <Eye className="w-3.5 h-3.5" />
                        Review Changes
                    </button>
                )}
            </div>
        </motion.div>
    );
}

// Helper to format completion message with basic markdown
function formatCompletionMessage(message: string): string {
    return message
        // Bold text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Code blocks
        .replace(/`([^`]+)`/g, '<code class="px-1 py-0.5 rounded bg-slate-100 text-slate-700 text-xs font-mono">$1</code>')
        // Line breaks
        .replace(/\n/g, '<br />')
        // Bullet points
        .replace(/^• /gm, '<span class="text-slate-400 mr-1">•</span>');
}
