"use client";

/**
 * TaskPlanView - Displays task breakdown with dependencies and progress
 * 
 * Shows:
 * - Task plan overview (strategy, agents involved)
 * - Individual tasks with status indicators
 * - Dependencies between tasks
 * - Extracted entities from user message
 * - Real-time status updates
 */

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
    ChevronDown,
    ChevronRight,
    CheckCircle2,
    Circle,
    Loader2,
    XCircle,
    AlertCircle,
    ShieldCheck,
    ArrowRight,
    Sparkles,
    ListChecks,
    Handshake,
    Megaphone,
    DollarSign,
    Calendar,
    Code,
} from "lucide-react";
import { cn } from "@/lib/utils";
import type {
    TaskPlanFeedItem,
    TaskInfo,
    TaskExecutionStatus,
    ExtractedEntity,
} from "./types";
import {
    TASK_STATUS_TEXT,
    TASK_STATUS_COLORS,
    TASK_STATUS_BG,
} from "./types";
import { AgentId } from "@/lib/config";

interface TaskPlanViewProps {
    taskPlan: TaskPlanFeedItem;
    defaultExpanded?: boolean;
}

// Agent icon mapping
const AGENT_ICONS: Record<string, React.FC<{ className?: string }>> = {
    partnerships: Handshake,
    marketing: Megaphone,
    finance: DollarSign,
    events: Calendar,
    developers: Code,
};

function getAgentIcon(agent: string) {
    const lowerAgent = agent.toLowerCase();
    return AGENT_ICONS[lowerAgent] || Sparkles;
}

// Status icon component
function TaskStatusIcon({ status }: { status: TaskExecutionStatus }) {
    switch (status) {
        case 'pending':
            return <Circle className="w-4 h-4 text-slate-300" />;
        case 'running':
            return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
        case 'completed':
            return <CheckCircle2 className="w-4 h-4 text-emerald-500" />;
        case 'failed':
            return <XCircle className="w-4 h-4 text-red-500" />;
        case 'skipped':
            return <AlertCircle className="w-4 h-4 text-amber-500" />;
        case 'approval_required':
            return <ShieldCheck className="w-4 h-4 text-purple-500" />;
        default:
            return <Circle className="w-4 h-4 text-slate-300" />;
    }
}

// Individual task row
function TaskRow({ task, isLast }: { task: TaskInfo; isLast: boolean }) {
    const [isExpanded, setIsExpanded] = useState(false);
    const AgentIcon = getAgentIcon(task.agent);

    return (
        <div className="relative">
            {/* Connecting line */}
            {!isLast && (
                <div className="absolute left-[11px] top-6 bottom-0 w-px bg-slate-200" />
            )}

            <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className={cn(
                    "flex items-start gap-3 p-2 rounded-md transition-colors",
                    task.status === 'running' && "bg-blue-50",
                    task.status === 'completed' && "bg-emerald-50/50",
                    task.status === 'failed' && "bg-red-50/50",
                )}
            >
                {/* Status Icon */}
                <div className="flex-shrink-0 mt-0.5">
                    <TaskStatusIcon status={task.status} />
                </div>

                {/* Task Content */}
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                        {/* Agent Badge */}
                        <span className={cn(
                            "inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs font-medium",
                            TASK_STATUS_BG[task.status],
                            TASK_STATUS_COLORS[task.status],
                        )}>
                            <AgentIcon className="w-3 h-3" />
                            {task.agent}
                        </span>

                        {/* Action */}
                        <span className="text-xs text-slate-500 font-mono">
                            {task.action}
                        </span>

                        {/* Approval Badge */}
                        {task.requires_approval && task.status !== 'completed' && (
                            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-xs bg-purple-100 text-purple-600">
                                <ShieldCheck className="w-3 h-3" />
                                Approval
                            </span>
                        )}
                    </div>

                    {/* Description */}
                    <p className="text-sm text-slate-700 mt-1">
                        {task.description}
                    </p>

                    {/* Dependencies */}
                    {task.depends_on.length > 0 && (
                        <div className="flex items-center gap-1 mt-1 text-xs text-slate-400">
                            <ArrowRight className="w-3 h-3" />
                            <span>Depends on: {task.depends_on.join(', ')}</span>
                        </div>
                    )}

                    {/* Result/Error */}
                    {task.status === 'completed' && task.result && (
                        <p className="text-xs text-emerald-600 mt-1">
                            ✓ {task.result}
                        </p>
                    )}
                    {task.status === 'failed' && task.error && (
                        <p className="text-xs text-red-600 mt-1">
                            ✗ {task.error}
                        </p>
                    )}

                    {/* Execution Time */}
                    {task.execution_time !== undefined && task.execution_time > 0 && (
                        <p className="text-xs text-slate-400 mt-1">
                            Completed in {task.execution_time.toFixed(2)}s
                        </p>
                    )}
                </div>
            </motion.div>
        </div>
    );
}

// Extracted entities display
function EntitiesSection({ entities }: { entities: ExtractedEntity[] }) {
    if (entities.length === 0) return null;

    return (
        <div className="mt-3 pt-3 border-t border-slate-100">
            <p className="text-xs text-slate-500 mb-2">Extracted from your message:</p>
            <div className="flex flex-wrap gap-1.5">
                {entities.map((entity, idx) => (
                    <span
                        key={idx}
                        className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-slate-100 text-slate-600"
                    >
                        <span className="font-medium text-slate-400 mr-1">{entity.type}:</span>
                        {String(entity.value)}
                    </span>
                ))}
            </div>
        </div>
    );
}

export function TaskPlanView({ taskPlan, defaultExpanded = true }: TaskPlanViewProps) {
    const [isExpanded, setIsExpanded] = useState(defaultExpanded);
    const { plan, status, completedTasks, failedTasks } = taskPlan;

    const totalTasks = plan.total_tasks;
    const progress = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0;

    // Compact view
    if (!isExpanded) {
        return (
            <motion.button
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                onClick={() => setIsExpanded(true)}
                className={cn(
                    "w-full flex items-center gap-3 px-3 py-2",
                    "rounded-md hover:bg-slate-100",
                    "transition-all duration-150 text-left group"
                )}
            >
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-slate-600" />
                <ListChecks className="w-4 h-4 text-slate-500" />
                <span className="text-sm font-medium text-slate-900">Task Plan</span>
                
                {/* Progress indicator */}
                <div className="flex items-center gap-2 ml-auto">
                    <span className="text-xs text-slate-500">
                        {completedTasks}/{totalTasks} tasks
                    </span>
                    <div className="w-16 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                        <div
                            className={cn(
                                "h-full rounded-full transition-all duration-300",
                                failedTasks > 0 ? "bg-red-500" : "bg-emerald-500"
                            )}
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                </div>
            </motion.button>
        );
    }

    // Expanded view
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-md overflow-hidden"
        >
            {/* Header */}
            <button
                onClick={() => setIsExpanded(false)}
                className="w-full flex items-center gap-2 p-3 text-left group"
            >
                <ChevronDown className="w-4 h-4 text-slate-400 group-hover:text-slate-600" />
                <ListChecks className="w-4 h-4 text-slate-500" />
                <span className="text-sm font-semibold text-slate-900">Task Plan</span>
                
                {/* Status badges */}
                <span className={cn(
                    "px-2 py-0.5 rounded text-xs font-medium",
                    plan.request_type === 'workflow' && "bg-blue-100 text-blue-700",
                    plan.request_type === 'question' && "bg-green-100 text-green-700",
                    plan.request_type === 'status_update' && "bg-amber-100 text-amber-700",
                )}>
                    {plan.request_type}
                </span>

                <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-600">
                    {plan.execution_strategy}
                </span>

                {/* Progress */}
                <div className="flex items-center gap-2 ml-auto">
                    <span className="text-xs text-slate-500">
                        {completedTasks}/{totalTasks}
                        {failedTasks > 0 && <span className="text-red-500 ml-1">({failedTasks} failed)</span>}
                    </span>
                    <div className="w-20 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                        <div
                            className={cn(
                                "h-full rounded-full transition-all duration-300",
                                failedTasks > 0 ? "bg-red-500" : "bg-emerald-500"
                            )}
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                </div>
            </button>

            {/* Tasks list */}
            <div className="px-3 pb-3">
                <div className="pl-2 space-y-1">
                    {plan.tasks.map((task, idx) => (
                        <TaskRow
                            key={task.id}
                            task={task}
                            isLast={idx === plan.tasks.length - 1}
                        />
                    ))}
                </div>

                {/* Extracted entities */}
                <EntitiesSection entities={plan.extracted_entities} />

                {/* Agents involved */}
                <div className="mt-3 pt-3 border-t border-slate-100">
                    <p className="text-xs text-slate-500 mb-2">Agents involved:</p>
                    <div className="flex gap-2">
                        {plan.target_agents.map(agent => {
                            const AgentIcon = getAgentIcon(agent);
                            return (
                                <span
                                    key={agent}
                                    className="inline-flex items-center gap-1 px-2 py-1 rounded bg-slate-100 text-xs text-slate-600"
                                >
                                    <AgentIcon className="w-3 h-3" />
                                    {agent}
                                </span>
                            );
                        })}
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
