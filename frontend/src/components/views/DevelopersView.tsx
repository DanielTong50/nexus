"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { GitBranch, GitPullRequest, AlertCircle, Plus } from "lucide-react";

const COLUMNS = [
    {
        title: "To Do",
        count: 3,
        issues: [
            { title: "Implement Auth0 Login", repo: "frontend", number: 142, tags: ["auth", "high-priority"] },
            { title: "Optimize Image Loading", repo: "frontend", number: 145, tags: ["performance"] },
        ]
    },
    {
        title: "In Progress",
        count: 2,
        issues: [
            { title: "Stripe Integration", repo: "backend", number: 89, tags: ["api", "payments"], assignee: "JD" },
            { title: "Refactor Chat Component", repo: "frontend", number: 150, tags: ["ui"], assignee: "DT" },
        ]
    },
    {
        title: "Done",
        count: 12,
        issues: [
            { title: "Fix Mobile Layout", repo: "frontend", number: 138, tags: ["bug"], isDone: true },
        ]
    }
];

export function DevelopersView() {
    return (
        <div className="max-w-6xl">
            {/* Header */}
            <div className="flex items-start justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-slate-900">
                        Developers
                    </h1>
                    <p className="text-slate-500 mt-1">
                        Track issues, PRs, and deployments.
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <Badge variant="outline" className="gap-1.5 px-3 py-1 font-normal">
                        <GitBranch className="h-3 w-3" />
                        main
                    </Badge>
                    <Badge className="bg-emerald-500 hover:bg-emerald-500 gap-1.5 px-3 py-1">
                        v2.4.0 Live
                    </Badge>
                </div>
            </div>

            {/* Kanban Board */}
            <div className="grid grid-cols-3 gap-6">
                {COLUMNS.map((column) => (
                    <div key={column.title}>
                        <div className="flex items-center justify-between mb-4 px-1">
                            <div className="flex items-center gap-2">
                                <h3 className="text-sm font-semibold text-slate-700">{column.title}</h3>
                                <span className="text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                                    {column.count}
                                </span>
                            </div>
                            <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-slate-400 hover:text-slate-600">
                                <Plus className="h-4 w-4" />
                            </Button>
                        </div>

                        <div className="space-y-3">
                            {column.issues.map((issue, idx) => (
                                <IssueCard key={idx} issue={issue} />
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

interface IssueCardProps {
    issue: {
        title: string;
        repo: string;
        number: number;
        tags: string[];
        assignee?: string;
        isDone?: boolean;
    };
}

function IssueCard({ issue }: IssueCardProps) {
    return (
        <Card className={`border border-slate-200 shadow-sm hover:border-slate-300 cursor-pointer transition-colors ${issue.isDone ? 'opacity-60' : ''}`}>
            <CardContent className="p-4">
                <div className="flex items-start justify-between gap-2 mb-3">
                    <span className="text-sm font-medium text-slate-900 leading-snug">
                        {issue.title}
                    </span>
                    {issue.isDone && (
                        <div className="h-2 w-2 rounded-full bg-emerald-500 mt-1.5 flex-shrink-0" />
                    )}
                </div>

                <div className="flex items-center gap-2 text-xs text-slate-400 mb-3">
                    {issue.repo === "backend" ? (
                        <GitPullRequest className="h-3 w-3" />
                    ) : (
                        <AlertCircle className="h-3 w-3" />
                    )}
                    <span>{issue.repo}/#{issue.number}</span>
                </div>

                <div className="flex items-center justify-between">
                    <div className="flex gap-1 flex-wrap">
                        {issue.tags.map((tag) => (
                            <span
                                key={tag}
                                className="px-1.5 py-0.5 bg-slate-100 text-slate-500 text-[10px] rounded uppercase font-medium"
                            >
                                {tag}
                            </span>
                        ))}
                    </div>
                    {issue.assignee && (
                        <Avatar className="h-6 w-6">
                            <AvatarFallback className="text-[10px] bg-slate-100 text-slate-600">
                                {issue.assignee}
                            </AvatarFallback>
                        </Avatar>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
