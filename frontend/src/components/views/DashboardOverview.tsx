"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
    Calendar,
    Users,
    DollarSign,
    CheckCircle2,
    ArrowRight,
    Zap,
    Target,
    MessageSquare,
    GitPullRequest,
    Megaphone,
    Handshake,
    Code,
    ChevronRight,
} from "lucide-react";

// Event Configuration
const EVENT = {
    name: "Blueprint 2026",
    tagline: "The Future of AI Hackathons",
    date: new Date("2026-02-15T09:00:00"),
    venue: "Tech Campus Building A",
    expectedAttendees: 500,
    registeredAttendees: 342,
};

// Metrics data (would come from API in production)
const METRICS = {
    partnerships: {
        totalRaised: 65000,
        goal: 100000,
        confirmedSponsors: 3,
        pendingSponsors: 2,
        recentActivity: "Anthropic confirmed as Gold Sponsor",
    },
    finance: {
        totalBudget: 250000,
        spent: 84320,
        pending: 8500,
    },
    marketing: {
        scheduledPosts: 12,
        publishedPosts: 28,
        engagement: 15420,
        followers: 4250,
    },
    events: {
        tasksCompleted: 18,
        totalTasks: 32,
        upcomingMilestone: "Venue Walkthrough",
        milestoneDate: "Jan 25",
    },
    developers: {
        openIssues: 8,
        closedThisWeek: 12,
        activePRs: 3,
        deployments: 5,
    },
};

// Recent activity feed
const RECENT_ACTIVITY = [
    { type: "partnership", message: "OpenAI added as Platinum Sponsor", time: "2 min ago", icon: Handshake },
    { type: "slack", message: "Reminder sent to marketing team", time: "15 min ago", icon: MessageSquare },
    { type: "task", message: "Venue deposit payment confirmed", time: "1 hour ago", icon: CheckCircle2 },
    { type: "github", message: "PR #150 merged: Chat Component Refactor", time: "2 hours ago", icon: GitPullRequest },
    { type: "marketing", message: "Instagram post scheduled for tomorrow", time: "3 hours ago", icon: Megaphone },
];

export function DashboardOverview() {
    const [countdown, setCountdown] = useState({ days: 0, hours: 0, minutes: 0, seconds: 0 });
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
        const timer = setInterval(() => {
            const now = new Date();
            const diff = EVENT.date.getTime() - now.getTime();

            if (diff > 0) {
                setCountdown({
                    days: Math.floor(diff / (1000 * 60 * 60 * 24)),
                    hours: Math.floor((diff / (1000 * 60 * 60)) % 24),
                    minutes: Math.floor((diff / 1000 / 60) % 60),
                    seconds: Math.floor((diff / 1000) % 60),
                });
            }
        }, 1000);

        return () => clearInterval(timer);
    }, []);

    const budgetSpent = (METRICS.finance.spent / METRICS.finance.totalBudget) * 100;

    return (
        <div className="max-w-6xl space-y-8">
            {/* Hero Section - Event Overview */}
            <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8 text-white">
                {/* Background Pattern */}
                <div className="absolute inset-0 opacity-10">
                    <div className="absolute inset-0" style={{
                        backgroundImage: `radial-gradient(circle at 25% 25%, white 1px, transparent 1px)`,
                        backgroundSize: '32px 32px'
                    }} />
                </div>

                <div className="relative z-10">
                    <div className="flex items-start justify-between">
                        <div>
                            <Badge className="bg-white/10 text-white border-white/20 mb-4 backdrop-blur-sm">
                                <Zap className="h-3 w-3 mr-1" />
                                Live Dashboard
                            </Badge>
                            <h1 className="text-4xl font-bold tracking-tight mb-2">
                                {EVENT.name}
                            </h1>
                            <p className="text-slate-300 text-lg mb-1">{EVENT.tagline}</p>
                            <div className="flex items-center gap-4 text-sm text-slate-400 mt-4">
                                <span className="flex items-center gap-1.5">
                                    <Calendar className="h-4 w-4" />
                                    {EVENT.date.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
                                </span>
                                <span className="flex items-center gap-1.5">
                                    <Target className="h-4 w-4" />
                                    {EVENT.venue}
                                </span>
                            </div>
                        </div>

                        {/* Countdown Timer */}
                        {mounted && (
                            <div className="text-right">
                                <p className="text-xs uppercase tracking-wider text-slate-400 mb-3">Countdown to Event</p>
                                <div className="flex gap-3">
                                    {[
                                        { value: countdown.days, label: 'Days' },
                                        { value: countdown.hours, label: 'Hours' },
                                        { value: countdown.minutes, label: 'Min' },
                                        { value: countdown.seconds, label: 'Sec' },
                                    ].map((item) => (
                                        <div key={item.label} className="text-center">
                                            <div className="bg-white/10 backdrop-blur-sm rounded-lg px-4 py-3 min-w-[60px] border border-white/10">
                                                <span className="text-2xl font-bold font-mono">
                                                    {String(item.value).padStart(2, '0')}
                                                </span>
                                            </div>
                                            <span className="text-[10px] uppercase tracking-wider text-slate-500 mt-1 block">
                                                {item.label}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Quick Stats Bar */}
                    <div className="flex items-center gap-8 mt-8 pt-6 border-t border-white/10">
                        <QuickStat
                            icon={Users}
                            value={EVENT.registeredAttendees}
                            label="Registered"
                            suffix={`/ ${EVENT.expectedAttendees}`}
                        />
                        <QuickStat
                            icon={DollarSign}
                            value={`$${(METRICS.partnerships.totalRaised / 1000).toFixed(0)}k`}
                            label="Raised"
                            suffix={`/ $${METRICS.partnerships.goal / 1000}k`}
                        />
                        <QuickStat
                            icon={CheckCircle2}
                            value={METRICS.events.tasksCompleted}
                            label="Tasks Done"
                            suffix={`/ ${METRICS.events.totalTasks}`}
                        />
                        <QuickStat
                            icon={Handshake}
                            value={METRICS.partnerships.confirmedSponsors}
                            label="Sponsors"
                            suffix="confirmed"
                        />
                    </div>
                </div>
            </div>

            {/* Progress Overview Cards */}
            <div className="grid grid-cols-4 gap-4">
                <ProgressCard
                    title="Funding Goal"
                    current={METRICS.partnerships.totalRaised}
                    target={METRICS.partnerships.goal}
                    format="currency"
                    color="emerald"
                    href="/partnerships"
                />
                <ProgressCard
                    title="Registration"
                    current={EVENT.registeredAttendees}
                    target={EVENT.expectedAttendees}
                    format="number"
                    color="blue"
                    href="/events"
                />
                <ProgressCard
                    title="Tasks Complete"
                    current={METRICS.events.tasksCompleted}
                    target={METRICS.events.totalTasks}
                    format="number"
                    color="violet"
                    href="/events"
                />
                <ProgressCard
                    title="Budget Used"
                    current={METRICS.finance.spent}
                    target={METRICS.finance.totalBudget}
                    format="currency"
                    color="amber"
                    href="/finance"
                />
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-3 gap-6">
                {/* Left Column - Category Summaries */}
                <div className="col-span-2 space-y-6">
                    {/* Partnerships & Finance Row */}
                    <div className="grid grid-cols-2 gap-4">
                        <CategoryCard
                            title="Partnerships"
                            icon={Handshake}
                            href="/partnerships"
                            stats={[
                                { label: "Confirmed", value: METRICS.partnerships.confirmedSponsors },
                                { label: "Pending", value: METRICS.partnerships.pendingSponsors },
                                { label: "Pipeline", value: `$${(METRICS.partnerships.goal / 1000).toFixed(0)}k` },
                            ]}
                            highlight={METRICS.partnerships.recentActivity}
                            highlightType="success"
                        />
                        <CategoryCard
                            title="Finance"
                            icon={DollarSign}
                            href="/finance"
                            stats={[
                                { label: "Budget", value: `$${(METRICS.finance.totalBudget / 1000).toFixed(0)}k` },
                                { label: "Spent", value: `$${(METRICS.finance.spent / 1000).toFixed(0)}k` },
                                { label: "Pending", value: `$${(METRICS.finance.pending / 1000).toFixed(1)}k` },
                            ]}
                            highlight={`${budgetSpent.toFixed(0)}% of budget utilized`}
                            highlightType="info"
                        />
                    </div>

                    {/* Marketing & Events Row */}
                    <div className="grid grid-cols-2 gap-4">
                        <CategoryCard
                            title="Marketing"
                            icon={Megaphone}
                            href="/marketing"
                            stats={[
                                { label: "Posts", value: METRICS.marketing.publishedPosts },
                                { label: "Scheduled", value: METRICS.marketing.scheduledPosts },
                                { label: "Engagement", value: `${(METRICS.marketing.engagement / 1000).toFixed(1)}k` },
                            ]}
                            highlight={`${METRICS.marketing.followers.toLocaleString()} followers`}
                            highlightType="info"
                        />
                        <CategoryCard
                            title="Events"
                            icon={Calendar}
                            href="/events"
                            stats={[
                                { label: "Complete", value: METRICS.events.tasksCompleted },
                                { label: "Remaining", value: METRICS.events.totalTasks - METRICS.events.tasksCompleted },
                                { label: "Next", value: METRICS.events.milestoneDate },
                            ]}
                            highlight={`Next: ${METRICS.events.upcomingMilestone}`}
                            highlightType="warning"
                        />
                    </div>

                    {/* Developers Card - Full Width */}
                    <CategoryCard
                        title="Developers"
                        icon={Code}
                        href="/developers"
                        stats={[
                            { label: "Open Issues", value: METRICS.developers.openIssues },
                            { label: "Closed (week)", value: METRICS.developers.closedThisWeek },
                            { label: "Active PRs", value: METRICS.developers.activePRs },
                            { label: "Deployments", value: METRICS.developers.deployments },
                        ]}
                        highlight="All systems operational"
                        highlightType="success"
                        fullWidth
                    />
                </div>

                {/* Right Column - Activity Feed */}
                <div className="space-y-6">
                    <Card className="border border-slate-200 shadow-sm">
                        <CardContent className="p-5">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="font-semibold text-slate-900 tracking-tight">Recent Activity</h3>
                                <Badge variant="outline" className="text-xs font-normal">
                                    Live
                                    <span className="ml-1.5 h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                                </Badge>
                            </div>
                            <div className="space-y-4">
                                {RECENT_ACTIVITY.map((activity, idx) => (
                                    <ActivityItem key={idx} activity={activity} />
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Team Online */}
                    <Card className="border border-slate-200 shadow-sm">
                        <CardContent className="p-5">
                            <h3 className="font-semibold text-slate-900 tracking-tight mb-4">Team Online</h3>
                            <div className="flex -space-x-2">
                                {['JD', 'SC', 'MR', 'AK', 'DT'].map((initials, idx) => (
                                    <Avatar key={idx} className="h-9 w-9 border-2 border-white ring-2 ring-emerald-500/20">
                                        <AvatarFallback className="text-xs bg-slate-100 text-slate-600">
                                            {initials}
                                        </AvatarFallback>
                                    </Avatar>
                                ))}
                                <div className="h-9 w-9 rounded-full bg-slate-100 border-2 border-white flex items-center justify-center">
                                    <span className="text-xs text-slate-500 font-medium">+8</span>
                                </div>
                            </div>
                            <p className="text-xs text-slate-500 mt-3">13 team members active</p>
                        </CardContent>
                    </Card>

                    {/* AI Assistant Prompt */}
                    <Card className="border border-slate-200 shadow-sm bg-gradient-to-br from-slate-50 to-white">
                        <CardContent className="p-5">
                            <div className="flex items-start gap-3">
                                <div className="h-8 w-8 rounded-lg bg-slate-900 flex items-center justify-center flex-shrink-0">
                                    <Zap className="h-4 w-4 text-white" />
                                </div>
                                <div>
                                    <h3 className="font-semibold text-slate-900 tracking-tight text-sm">Nexus AI</h3>
                                    <p className="text-xs text-slate-500 mt-1">
                                        Use the chat panel to manage sponsors, send Slack messages, or get event updates.
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}

// Sub-components

function QuickStat({ icon: Icon, value, label, suffix }: {
    icon: React.ElementType;
    value: string | number;
    label: string;
    suffix?: string;
}) {
    return (
        <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-white/10 flex items-center justify-center">
                <Icon className="h-5 w-5 text-white/80" />
            </div>
            <div>
                <div className="flex items-baseline gap-1">
                    <span className="text-xl font-bold">{value}</span>
                    {suffix && <span className="text-sm text-slate-400">{suffix}</span>}
                </div>
                <span className="text-xs text-slate-400">{label}</span>
            </div>
        </div>
    );
}

function ProgressCard({ title, current, target, format, color, href }: {
    title: string;
    current: number;
    target: number;
    format: 'currency' | 'number';
    color: 'emerald' | 'blue' | 'violet' | 'amber';
    href: string;
}) {
    const percentage = Math.min((current / target) * 100, 100);
    const formatValue = (val: number) => {
        if (format === 'currency') return `$${(val / 1000).toFixed(0)}k`;
        return val.toString();
    };

    const colorClasses = {
        emerald: 'text-emerald-600 bg-emerald-500',
        blue: 'text-blue-600 bg-blue-500',
        violet: 'text-violet-600 bg-violet-500',
        amber: 'text-amber-600 bg-amber-500',
    };

    return (
        <Link href={href}>
            <Card className="border border-slate-200 shadow-sm hover:shadow-md hover:border-slate-300 transition-all cursor-pointer group">
                <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-3">
                        <span className="text-sm text-slate-500">{title}</span>
                        <ChevronRight className="h-4 w-4 text-slate-300 group-hover:text-slate-500 group-hover:translate-x-0.5 transition-all" />
                    </div>
                    <div className="flex items-baseline gap-1 mb-3">
                        <span className={`text-2xl font-bold tracking-tight ${colorClasses[color].split(' ')[0]}`}>
                            {formatValue(current)}
                        </span>
                        <span className="text-sm text-slate-400">/ {formatValue(target)}</span>
                    </div>
                    <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
                        <div
                            className={`h-full rounded-full transition-all duration-500 ${colorClasses[color].split(' ')[1]}`}
                            style={{ width: `${percentage}%` }}
                        />
                    </div>
                    <span className="text-xs text-slate-400 mt-2 block">{percentage.toFixed(0)}% complete</span>
                </CardContent>
            </Card>
        </Link>
    );
}

function CategoryCard({ title, icon: Icon, href, stats, highlight, highlightType, fullWidth }: {
    title: string;
    icon: React.ElementType;
    href: string;
    stats: { label: string; value: string | number }[];
    highlight: string;
    highlightType: 'success' | 'warning' | 'info';
    fullWidth?: boolean;
}) {
    const highlightColors = {
        success: 'text-emerald-600 bg-emerald-50',
        warning: 'text-amber-600 bg-amber-50',
        info: 'text-blue-600 bg-blue-50',
    };

    return (
        <Link href={href}>
            <Card className="border border-slate-200 shadow-sm hover:shadow-md hover:border-slate-300 transition-all cursor-pointer group h-full">
                <CardContent className="p-5">
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-2.5">
                            <div className="h-8 w-8 rounded-lg bg-slate-100 flex items-center justify-center group-hover:bg-slate-200 transition-colors">
                                <Icon className="h-4 w-4 text-slate-600" />
                            </div>
                            <h3 className="font-semibold text-slate-900 tracking-tight">{title}</h3>
                        </div>
                        <ArrowRight className="h-4 w-4 text-slate-300 group-hover:text-slate-500 group-hover:translate-x-0.5 transition-all" />
                    </div>

                    <div className={`grid gap-4 mb-4 ${fullWidth ? 'grid-cols-4' : 'grid-cols-3'}`}>
                        {stats.map((stat) => (
                            <div key={stat.label}>
                                <div className="text-lg font-semibold text-slate-900">{stat.value}</div>
                                <div className="text-xs text-slate-500">{stat.label}</div>
                            </div>
                        ))}
                    </div>

                    <div className={`text-xs px-2 py-1 rounded-md inline-block ${highlightColors[highlightType]}`}>
                        {highlight}
                    </div>
                </CardContent>
            </Card>
        </Link>
    );
}

function ActivityItem({ activity }: {
    activity: { type: string; message: string; time: string; icon: React.ElementType };
}) {
    const Icon = activity.icon;
    return (
        <div className="flex items-start gap-3">
            <div className="h-7 w-7 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                <Icon className="h-3.5 w-3.5 text-slate-500" />
            </div>
            <div className="flex-1 min-w-0">
                <p className="text-sm text-slate-700 leading-snug">{activity.message}</p>
                <span className="text-xs text-slate-400">{activity.time}</span>
            </div>
        </div>
    );
}
