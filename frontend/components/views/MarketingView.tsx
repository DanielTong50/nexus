"use client";

import React from "react";
import {
    MoreHorizontal,
    FileText,
    Megaphone,
    Calendar,
    Download,
    TrendingUp,
    Clock,
    Palette
} from "lucide-react";
import { mockEvents } from "@/lib/config";
import { useEvent } from "@/lib/event-context";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

export function MarketingView() {
    const { eventId } = useEvent();
    const currentEvent = mockEvents.find(e => e.id === eventId);

    if (!currentEvent) return null;

    // --- Gantt Chart Logic ---
    const campaigns = currentEvent.marketingCampaigns || [];

    // Determine overall timeline range
    // Default to current month +/- 1 month if no campaigns, else use campaign min/max with buffer
    const allDates = campaigns.flatMap(c => [new Date(c.startDate).getTime(), new Date(c.endDate).getTime()]);
    const minDate = allDates.length ? Math.min(...allDates) : Date.now() - 2592000000; // -30 days
    const maxDate = allDates.length ? Math.max(...allDates) : Date.now() + 5184000000; // +60 days

    // Add buffer (15 days before start, 15 days after end)
    const chartStart = minDate - 1296000000;
    const chartEnd = maxDate + 1296000000;
    const totalDuration = chartEnd - chartStart;

    // Helper to position bars
    const getPosition = (start: string, end: string) => {
        const startDate = new Date(start).getTime();
        const endDate = new Date(end).getTime();
        const left = ((startDate - chartStart) / totalDuration) * 100;
        const width = ((endDate - startDate) / totalDuration) * 100;
        return { left: `${left}%`, width: `${width}%` };
    };

    // Helper for status colors
    const getStatusStyle = (status: string) => {
        switch (status) {
            case "active": return "bg-green-500 text-white hover:bg-green-600";
            case "completed": return "bg-blue-500 text-white hover:bg-blue-600";
            case "planned": return "bg-gray-400 text-white hover:bg-gray-500";
            case "paused": return "bg-yellow-500 text-white hover:bg-yellow-600";
            default: return "bg-slate-500";
        }
    };

    // Generate month markers
    const months = [];
    let currentDate = new Date(chartStart);
    const endDateObj = new Date(chartEnd);

    while (currentDate <= endDateObj) {
        months.push(new Date(currentDate));
        currentDate.setMonth(currentDate.getMonth() + 1);
    }

    return (
        <div className="flex-1 p-6 space-y-8 max-w-[1600px] mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Marketing Campaigns</h1>
                    <p className="text-muted-foreground">
                        Plan and track marketing execution for <span className="font-semibold text-foreground">{currentEvent.name}</span>
                    </p>
                </div>
                <Button size="sm" className="gap-1.5">
                    <Megaphone className="h-4 w-4" />
                    New Campaign
                </Button>
            </div>

            {/* Gantt Chart Section */}
            <Card className="overflow-hidden border-2 border-muted/20">
                <CardHeader className="bg-muted/5 pb-4 border-b">
                    <div className="flex items-center justify-between">
                        <CardTitle className="text-sm font-medium flex items-center gap-2">
                            <Calendar className="h-4 w-4 text-primary" />
                            Campaign Timeline
                        </CardTitle>
                        <div className="flex gap-2">
                            {["Planned", "Active", "Completed"].map(status => (
                                <Badge key={status} variant="outline" className="text-[10px] font-normal text-muted-foreground">
                                    <div className={`h-2 w-2 rounded-full mr-1.5 ${status === "Planned" ? "bg-gray-400" :
                                        status === "Active" ? "bg-green-500" : "bg-blue-500"
                                        }`} />
                                    {status}
                                </Badge>
                            ))}
                        </div>
                    </div>
                </CardHeader>
                <CardContent className="p-0 overflow-x-auto">
                    <div className="min-w-[800px] p-6">
                        {/* Timeline Header */}
                        <div className="flex border-b mb-4 pb-2 relative h-8">
                            {months.map((month, idx) => {
                                const left = ((month.getTime() - chartStart) / totalDuration) * 100;
                                if (left < 0 || left > 100) return null;
                                return (
                                    <div
                                        key={idx}
                                        className="absolute text-xs font-semibold text-muted-foreground border-l pl-2 h-full flex items-center"
                                        style={{ left: `${left}%` }}
                                    >
                                        {month.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                                    </div>
                                );
                            })}
                        </div>

                        {/* Campaign Lines */}
                        <div className="space-y-6 relative">
                            {/* Vertical grid lines helper (optional) */}
                            <div className="absolute inset-0 pointer-events-none">
                                {months.map((month, idx) => {
                                    const left = ((month.getTime() - chartStart) / totalDuration) * 100;
                                    if (left < 0 || left > 100) return null;
                                    return (
                                        <div
                                            key={idx}
                                            className="absolute top-0 bottom-0 border-l border-dashed border-muted/20"
                                            style={{ left: `${left}%` }}
                                        />
                                    );
                                })}
                            </div>

                            {campaigns.length === 0 ? (
                                <div className="text-center py-10 text-muted-foreground italic">
                                    No marketing campaigns scheduled.
                                </div>
                            ) : (
                                campaigns.map((campaign) => {
                                    const { left, width } = getPosition(campaign.startDate, campaign.endDate);
                                    return (
                                        <div key={campaign.id} className="relative h-14 group">
                                            {/* Bar */}
                                            <div
                                                className={`absolute top-6 h-6 rounded-md shadow-sm border border-white/20 flex items-center px-3 cursor-pointer transition-transform hover:scale-[1.01] ${getStatusStyle(campaign.status)}`}
                                                style={{ left, width }}
                                            >
                                                <span className="text-xs font-semibold truncate text-white drop-shadow-md">
                                                    {campaign.name}
                                                </span>
                                            </div>

                                            {/* Label / Platform - positioned above or to left */}
                                            <div
                                                className="absolute top-0 text-[10px] font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-1.5"
                                                style={{ left }}
                                            >
                                                <Badge variant="secondary" className="h-4 p-0 px-1 text-[9px] rounded-sm uppercase">{campaign.platform}</Badge>
                                                {campaign.startDate} - {campaign.endDate}
                                            </div>
                                        </div>
                                    );
                                })
                            )}
                        </div>
                    </div>
                </CardContent>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Files */}
                <div className="lg:col-span-2 space-y-4">
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        <FileText className="h-5 w-5 text-muted-foreground" />
                        Campaign Assets
                    </h2>

                    {/* Marketing specific files */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <Card className="hover:border-primary/50 cursor-pointer transition-colors group border-dashed">
                            <CardContent className="p-4 flex flex-col items-center justify-center text-center py-8 text-muted-foreground gap-2">
                                <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center">
                                    <Download className="h-5 w-5 opacity-50" />
                                </div>
                                <p className="text-sm">Upload new asset</p>
                            </CardContent>
                        </Card>

                        {currentEvent.marketingFiles?.map((file, idx) => (
                            <Card key={idx} className="hover:border-primary/50 cursor-pointer transition-colors group">
                                <CardContent className="p-4 flex items-start gap-3">
                                    <div className={`p-2 rounded-md ${file.type === 'figma' ? 'bg-purple-50 text-purple-600' :
                                            'bg-blue-50 text-blue-600'
                                        }`}>
                                        {file.type === 'figma' ? <Palette className="h-5 w-5" /> : <FileText className="h-5 w-5" />}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="font-medium truncate group-hover:text-primary transition-colors">
                                            {file.name}
                                        </p>
                                        <p className="text-xs text-muted-foreground uppercase mt-0.5">
                                            {file.type === 'figma' ? 'Design File' : 'Video Script'}
                                        </p>
                                    </div>
                                    <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground">
                                        <Download className="h-4 w-4" />
                                    </Button>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </div>

                {/* Right Column: Timeline (Tasks) */}
                <div className="space-y-4">
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        <Clock className="h-5 w-5 text-muted-foreground" />
                        Upcoming Content
                    </h2>
                    <Card>
                        <CardContent className="p-0">
                            <div className="divide-y">
                                {/* Filter for marketing related tasks if possible, or just show all for now */}
                                {currentEvent.timeline?.map((item, idx) => (
                                    <div key={idx} className="p-4 flex gap-4 hover:bg-muted/20 transition-colors">
                                        <div className="flex flex-col items-center min-w-[3rem]">
                                            <span className="text-xs text-muted-foreground font-medium uppercase">
                                                {new Date(item.date).toLocaleDateString('en-US', { month: 'short' })}
                                            </span>
                                            <span className="text-lg font-bold">
                                                {new Date(item.date).getDate()}
                                            </span>
                                        </div>
                                        <div>
                                            <p className="font-medium text-sm">{item.title}</p>
                                            <div className="flex items-center gap-2 mt-1">
                                                <Badge
                                                    variant="secondary"
                                                    className={cn("text-[10px] px-1.5 h-5", item.type === 'milestone' ? "bg-purple-100 text-purple-700" : "bg-gray-100 text-gray-700")}
                                                >
                                                    {item.type}
                                                </Badge>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>

            <Separator />

            {/* Event Summary */}
            <div className="bg-muted/30 rounded-lg p-6 border border-border/50">
                <h3 className="text-sm font-semibold text-foreground mb-2 flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
                    AI Summary
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                    {currentEvent.summary || "No summary available for this event."}
                </p>
            </div>
        </div>
    );
}
