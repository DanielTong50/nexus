"use client";

import { useState, useEffect } from "react";
import {
    ArrowUpRight,
    ArrowDownRight,
    Clock,
    MessageSquare,
    FileSpreadsheet,
    GitPullRequest,
    GitCommit,
    Calendar,
    Users,
    DollarSign,
    CheckCircle,
    Circle,
    ChevronRight,
} from "lucide-react";

// Metrics Data
const METRICS = [
    { label: "Total Raised", value: "$65,000", subtext: "of $100k target", trend: "up" },
    { label: "Active Partners", value: "5", subtext: "3 pending outreach", trend: null },
    { label: "Registrations", value: "342", subtext: "of 500 target", trend: "up" },
    { label: "Tasks Complete", value: "18/32", subtext: "56% complete", trend: null },
];

// Recent Activity
const ACTIVITY = [
    { type: "slack", message: "OpenAI confirmed as Gold Sponsor", channel: "#partnerships", time: "2m ago" },
    { type: "sheets", message: "Added Stripe to sponsor pipeline", channel: "Partnerships Sheet", time: "15m ago" },
    { type: "github", message: "PR merged: SSE streaming for agents", channel: "nexus/backend", time: "1h ago" },
    { type: "calendar", message: "Venue walkthrough scheduled", channel: "Tomorrow, 2:00 PM", time: "2h ago" },
];

// Sponsor Pipeline
const SPONSORS = [
    { company: "Anthropic", tier: "Platinum", amount: "$25,000", status: "confirmed" },
    { company: "OpenAI", tier: "Gold", amount: "$15,000", status: "confirmed" },
    { company: "Stripe", tier: "Gold", amount: "$15,000", status: "pending" },
    { company: "Vercel", tier: "Silver", amount: "$10,000", status: "confirmed" },
];

// Dev Activity
const DEV_STATS = { commits: 47, prs: 12, issues: 8 };
const RECENT_PRS = [
    { title: "feat: SSE streaming for agents", author: "danieltong", status: "merged" },
    { title: "fix: MongoDB connection pool", author: "sarahc", status: "merged" },
    { title: "chore: Update dependencies", author: "mikr", status: "open" },
];

// Upcoming
const UPCOMING = [
    { title: "Venue Walkthrough", time: "Tomorrow, 2:00 PM" },
    { title: "Sponsor Call - Stripe", time: "Jan 22, 10:00 AM" },
    { title: "Marketing Review", time: "Jan 23, 3:00 PM" },
];

export function OverviewView() {
    const [currentTime, setCurrentTime] = useState<string>("");

    useEffect(() => {
        const updateTime = () => setCurrentTime(new Date().toLocaleTimeString());
        updateTime();
        const timer = setInterval(updateTime, 1000);
        return () => clearInterval(timer);
    }, []);

    return (
        <div className="space-y-6">
            {/* Status Bar */}
            <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-4">
                    <span className="text-gray-900 font-medium">System Status</span>
                    <div className="flex items-center gap-1.5">
                        <span className="h-2 w-2 rounded-full bg-green-500"></span>
                        <span className="text-gray-500">All systems operational</span>
                    </div>
                </div>
                <div className="flex items-center gap-1.5 text-gray-400">
                    <Clock className="h-3.5 w-3.5" />
                    <span className="font-mono text-xs">{currentTime}</span>
                </div>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-4 gap-4">
                {METRICS.map((metric) => (
                    <div
                        key={metric.label}
                        className="bg-white border border-gray-200 rounded-lg p-4"
                    >
                        <div className="text-xs text-gray-500 mb-1">{metric.label}</div>
                        <div className="flex items-baseline gap-2">
                            <span className="text-2xl font-semibold text-gray-900">{metric.value}</span>
                            {metric.trend && (
                                <span className={`flex items-center text-xs ${metric.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                                    {metric.trend === 'up' ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
                                </span>
                            )}
                        </div>
                        <div className="text-xs text-gray-400 mt-1">{metric.subtext}</div>
                    </div>
                ))}
            </div>

            {/* Main Grid */}
            <div className="grid grid-cols-3 gap-4">
                {/* Activity Feed */}
                <div className="col-span-2 bg-white border border-gray-200 rounded-lg">
                    <div className="px-4 py-3 border-b border-gray-200">
                        <span className="text-sm font-medium text-gray-900">Recent Activity</span>
                    </div>
                    <div className="divide-y divide-gray-100">
                        {ACTIVITY.map((item, idx) => (
                            <div key={idx} className="px-4 py-3 flex items-start gap-3">
                                <div className="mt-0.5">
                                    {item.type === 'slack' && <MessageSquare className="h-4 w-4 text-gray-400" />}
                                    {item.type === 'sheets' && <FileSpreadsheet className="h-4 w-4 text-gray-400" />}
                                    {item.type === 'github' && <GitPullRequest className="h-4 w-4 text-gray-400" />}
                                    {item.type === 'calendar' && <Calendar className="h-4 w-4 text-gray-400" />}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm text-gray-900">{item.message}</p>
                                    <p className="text-xs text-gray-400 mt-0.5">{item.channel}</p>
                                </div>
                                <span className="text-xs text-gray-400 whitespace-nowrap">{item.time}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Upcoming */}
                <div className="bg-white border border-gray-200 rounded-lg">
                    <div className="px-4 py-3 border-b border-gray-200">
                        <span className="text-sm font-medium text-gray-900">Upcoming</span>
                    </div>
                    <div className="divide-y divide-gray-100">
                        {UPCOMING.map((item, idx) => (
                            <div key={idx} className="px-4 py-3">
                                <p className="text-sm text-gray-900">{item.title}</p>
                                <p className="text-xs text-gray-400 mt-0.5 flex items-center gap-1">
                                    <Calendar className="h-3 w-3" />
                                    {item.time}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Sponsor Pipeline */}
            <div className="bg-white border border-gray-200 rounded-lg">
                <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-900">Sponsor Pipeline</span>
                    <button className="text-xs text-gray-500 hover:text-gray-900 flex items-center gap-1">
                        View all <ChevronRight className="h-3 w-3" />
                    </button>
                </div>
                <table className="w-full text-sm">
                    <thead>
                        <tr className="border-b border-gray-100 bg-gray-50">
                            <th className="text-left py-2 px-4 font-medium text-gray-500 text-xs">Company</th>
                            <th className="text-left py-2 px-4 font-medium text-gray-500 text-xs">Tier</th>
                            <th className="text-right py-2 px-4 font-medium text-gray-500 text-xs">Amount</th>
                            <th className="text-left py-2 px-4 font-medium text-gray-500 text-xs">Status</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {SPONSORS.map((sponsor, idx) => (
                            <tr key={idx} className="hover:bg-gray-50">
                                <td className="py-2.5 px-4 text-gray-900">{sponsor.company}</td>
                                <td className="py-2.5 px-4">
                                    <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">
                                        {sponsor.tier}
                                    </span>
                                </td>
                                <td className="py-2.5 px-4 text-right font-mono text-gray-900">{sponsor.amount}</td>
                                <td className="py-2.5 px-4">
                                    <span className={`flex items-center gap-1.5 text-xs ${sponsor.status === 'confirmed' ? 'text-green-600' : 'text-amber-600'}`}>
                                        {sponsor.status === 'confirmed' ? <CheckCircle className="h-3 w-3" /> : <Circle className="h-3 w-3" />}
                                        {sponsor.status === 'confirmed' ? 'Confirmed' : 'Pending'}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Dev Stats & Quick Actions */}
            <div className="grid grid-cols-2 gap-4">
                {/* Dev Stats */}
                <div className="bg-white border border-gray-200 rounded-lg">
                    <div className="px-4 py-3 border-b border-gray-200">
                        <span className="text-sm font-medium text-gray-900">Dev Activity</span>
                    </div>
                    <div className="p-4">
                        <div className="grid grid-cols-3 gap-4 mb-4">
                            <div className="text-center p-3 bg-gray-50 rounded-lg">
                                <div className="flex items-center justify-center gap-1.5 mb-1">
                                    <GitCommit className="h-3.5 w-3.5 text-gray-400" />
                                    <span className="text-xl font-semibold text-gray-900">{DEV_STATS.commits}</span>
                                </div>
                                <span className="text-xs text-gray-500">Commits</span>
                            </div>
                            <div className="text-center p-3 bg-gray-50 rounded-lg">
                                <div className="flex items-center justify-center gap-1.5 mb-1">
                                    <GitPullRequest className="h-3.5 w-3.5 text-gray-400" />
                                    <span className="text-xl font-semibold text-gray-900">{DEV_STATS.prs}</span>
                                </div>
                                <span className="text-xs text-gray-500">Pull Requests</span>
                            </div>
                            <div className="text-center p-3 bg-gray-50 rounded-lg">
                                <div className="flex items-center justify-center gap-1.5 mb-1">
                                    <Circle className="h-3.5 w-3.5 text-gray-400" />
                                    <span className="text-xl font-semibold text-gray-900">{DEV_STATS.issues}</span>
                                </div>
                                <span className="text-xs text-gray-500">Open Issues</span>
                            </div>
                        </div>
                        <div className="space-y-2">
                            <p className="text-xs font-medium text-gray-500">Recent Pull Requests</p>
                            {RECENT_PRS.map((pr, idx) => (
                                <div key={idx} className="flex items-center gap-2 text-sm py-1">
                                    <span className={`h-2 w-2 rounded-full ${pr.status === 'merged' ? 'bg-purple-500' : 'bg-green-500'}`} />
                                    <span className="text-gray-700 truncate flex-1">{pr.title}</span>
                                    <span className="text-xs text-gray-400">@{pr.author}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="bg-white border border-gray-200 rounded-lg">
                    <div className="px-4 py-3 border-b border-gray-200">
                        <span className="text-sm font-medium text-gray-900">Quick Actions</span>
                    </div>
                    <div className="p-4">
                        <p className="text-sm text-gray-500 mb-4">
                            Use the AI assistant to perform actions across all connected tools.
                        </p>
                        <div className="grid grid-cols-2 gap-2">
                            <ActionButton icon={DollarSign} label="Add Sponsor" />
                            <ActionButton icon={MessageSquare} label="Post to Slack" />
                            <ActionButton icon={Calendar} label="Schedule Meeting" />
                            <ActionButton icon={Users} label="Send Invite" />
                        </div>
                        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                            <p className="text-xs text-gray-500">
                                <span className="font-medium text-gray-700">Tip:</span> Try &quot;Add Anthropic as platinum sponsor at $25,000&quot;
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function ActionButton({ icon: Icon, label }: { icon: React.ElementType; label: string }) {
    return (
        <button className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-colors">
            <Icon className="h-4 w-4 text-gray-400" />
            {label}
        </button>
    );
}
