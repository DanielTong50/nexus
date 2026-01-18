"use client";

import React from "react";
import {
    MoreHorizontal,
    FileText,
    DollarSign,
    Calendar,
    CheckCircle,
    TrendingUp,
    Download,
    Clock
} from "lucide-react";
import { mockPartners, mockEvents, type Partner } from "@/lib/config";
import { useEvent } from "@/lib/event-context";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

export function FinanceView() {
    const { eventId } = useEvent();

    // Get current event data
    const currentEvent = mockEvents.find(e => e.id === eventId);

    // Filter partners by selected event (for MOU tracking)
    // Only include sponsors/partners, not judges/mentors for finance view usually
    const partners = mockPartners.filter((p) => p.eventId === eventId && (p.category === 'sponsor' || p.category === 'partner'));

    // Calculate totals
    const totalRaised = partners.reduce((sum, p) => sum + p.amount, 0);
    const fundingGoal = currentEvent?.targets?.funding?.target || 10000;
    const progress = (totalRaised / fundingGoal) * 100;

    const getMOUStatusStyle = (status: Partner["mouStatus"]) => {
        switch (status) {
            case "paid": return "bg-green-50 text-green-700 border-green-200";
            case "signed": return "bg-blue-50 text-blue-700 border-blue-200";
            case "sent": return "bg-yellow-50 text-yellow-700 border-yellow-200";
            case "followed-up": return "bg-purple-50 text-purple-700 border-purple-200";
            default: return "bg-gray-100 text-gray-700 border-gray-200";
        }
    };

    if (!currentEvent) return null;

    return (
        <div className="flex-1 p-6 space-y-8 max-w-[1600px] mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Finance & Budget</h1>
                    <p className="text-muted-foreground">
                        Manage funding, MOUs, and financial tracking for <span className="font-semibold text-foreground">{currentEvent.name}</span>
                    </p>
                </div>
                <Button size="sm" className="gap-1.5">
                    <DollarSign className="h-4 w-4" />
                    New Transaction
                </Button>
            </div>

            {/* Metric Targets (Funding) */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="md:col-span-2">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground flex justify-between">
                            Funding Progress
                            <TrendingUp className="h-4 w-4 text-green-500" />
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-end justify-between mb-4">
                            <div>
                                <div className="text-4xl font-bold flex items-baseline gap-1">
                                    ${totalRaised.toLocaleString()}
                                    <span className="text-lg text-muted-foreground font-normal">
                                        / ${fundingGoal.toLocaleString()}
                                    </span>
                                </div>
                                <p className="text-sm text-muted-foreground mt-1">
                                    Total raised from {partners.length} partners
                                </p>
                            </div>
                            <div className="text-right">
                                <span className="text-2xl font-bold text-primary">
                                    {Math.round(progress)}%
                                </span>
                                <span className="text-xs text-muted-foreground block">of goal</span>
                            </div>
                        </div>
                        <Progress value={Math.min(progress, 100)} className="h-3" />
                    </CardContent>
                </Card>

                {/* Quick Stats */}
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">Budget Status</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="flex justify-between items-center">
                            <span className="text-sm">Total Budget</span>
                            <span className="font-semibold">${currentEvent.budget.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-sm">Spent</span>
                            <span className="font-semibold text-red-500">${currentEvent.spent.toLocaleString()}</span>
                        </div>
                        <Separator />
                        <div className="flex justify-between items-center">
                            <span className="text-sm font-medium">Remaining</span>
                            <span className="font-bold text-green-600">${(currentEvent.budget - currentEvent.spent).toLocaleString()}</span>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* MOU Status Table */}
            <div className="space-y-4">
                <h2 className="text-lg font-semibold">MOU Status Tracking</h2>
                <Card>
                    <CardContent className="p-0">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b bg-muted/30">
                                    <th className="text-left font-medium text-muted-foreground p-3 pl-4">Company</th>
                                    <th className="text-left font-medium text-muted-foreground p-3">MOU Details</th>
                                    <th className="text-left font-medium text-muted-foreground p-3">Status</th>
                                    <th className="text-left font-medium text-muted-foreground p-3">Amount</th>
                                    <th className="text-left font-medium text-muted-foreground p-3">Last Update</th>
                                    <th className="p-3"></th>
                                </tr>
                            </thead>
                            <tbody>
                                {partners.length === 0 ? (
                                    <tr>
                                        <td colSpan={6} className="p-8 text-center text-muted-foreground">
                                            No financial records found.
                                        </td>
                                    </tr>
                                ) : (
                                    partners.map((partner) => (
                                        <tr key={partner.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                                            <td className="p-3 pl-4 font-medium">{partner.name}</td>
                                            <td className="p-3 text-muted-foreground">
                                                Standard Sponsorship Agreement
                                            </td>
                                            <td className="p-3">
                                                <Badge variant="outline" className={cn("capitalize", getMOUStatusStyle(partner.mouStatus))}>
                                                    {partner.mouStatus?.replace('-', ' ') || 'Pending'}
                                                </Badge>
                                            </td>
                                            <td className="p-3 font-medium">
                                                ${partner.amount.toLocaleString()}
                                            </td>
                                            <td className="p-3 text-muted-foreground text-xs">
                                                {partner.lastContact}
                                            </td>
                                            <td className="p-3 text-right">
                                                <Button variant="ghost" size="icon" className="h-8 w-8">
                                                    <Download className="h-4 w-4" />
                                                </Button>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </CardContent>
                </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Files & Timeline */}
                <div className="lg:col-span-2 space-y-8">
                    {/* Relevant Files */}
                    <div className="space-y-4">
                        <h2 className="text-lg font-semibold flex items-center gap-2">
                            <FileText className="h-5 w-5 text-muted-foreground" />
                            Relevant Documents
                        </h2>
                        {currentEvent.files && currentEvent.files.length > 0 ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {currentEvent.files.map((file, idx) => (
                                    <div key={idx} className="flex items-center justify-between p-3 rounded-lg border bg-card hover:bg-accent/5 transition-colors cursor-pointer group">
                                        <div className="flex items-center gap-3 overflow-hidden">
                                            <div className="h-10 w-10 rounded-md bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
                                                <FileText className="h-5 w-5" />
                                            </div>
                                            <div className="min-w-0">
                                                <p className="font-medium truncate group-hover:text-primary transition-colors">{file.name}</p>
                                                <p className="text-xs text-muted-foreground uppercase">{file.type}</p>
                                            </div>
                                        </div>
                                        <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <Download className="h-4 w-4" />
                                        </Button>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="p-8 border border-dashed rounded-lg text-center text-muted-foreground">
                                No files uploaded yet.
                            </div>
                        )}
                    </div>
                </div>

                {/* Right Column: Timeline */}
                <div className="space-y-4">
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        <Clock className="h-5 w-5 text-muted-foreground" />
                        Upcoming Tasks
                    </h2>
                    <Card>
                        <CardContent className="p-0">
                            <div className="divide-y">
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
                                                {new Date(item.date) < new Date() && (
                                                    <span className="text-[10px] text-red-500 font-medium">Overdue</span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                                {!currentEvent.timeline?.length && (
                                    <div className="p-4 text-center text-sm text-muted-foreground">
                                        No upcoming tasks.
                                    </div>
                                )}
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
