"use client";

import React from "react";
import {
    MoreHorizontal,
    FileText,
    Users,
    Briefcase,
    Download,
    Clock
} from "lucide-react";
import { mockPartners, mockEvents, type Partner } from "@/lib/config";
import { useEvent } from "@/lib/event-context";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
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

export function PartnershipsView() {
    const { eventId } = useEvent();

    // Get current event data
    const currentEvent = mockEvents.find(e => e.id === eventId);

    // Filter partners by selected event
    const partners = mockPartners.filter((p) => p.eventId === eventId);

    // Get stats
    const signedCount = partners.filter(p => p.status === 'signed').length;
    const agreedCount = partners.filter(p => p.status === 'agreed').length;
    const inTalksCount = partners.filter(p => p.status === 'in_talks').length;
    const rejectedCount = partners.filter(p => p.status === 'rejected').length;

    // Helper for status styles
    const getStatusStyle = (status: Partner["status"]) => {
        switch (status) {
            case "signed": return "bg-green-50 text-green-700 border-green-200";
            case "agreed": return "bg-blue-50 text-blue-700 border-blue-200"; // Agreed = verbal match?
            case "in_talks": return "bg-yellow-50 text-yellow-700 border-yellow-200";
            case "rejected": return "bg-red-50 text-red-700 border-red-200";
            default: return "bg-gray-100 text-gray-700 border-gray-200";
        }
    };

    // Helper for status label formatting
    const getStatusLabel = (status: Partner["status"]) => {
        switch (status) {
            case "in_talks": return "In Talks";
            default: return status.charAt(0).toUpperCase() + status.slice(1);
        }
    }

    if (!currentEvent) return null;

    return (
        <div className="flex-1 p-6 space-y-8 max-w-[1600px] mx-auto">
            {/* Header with quick stats */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Partnerships</h1>
                    <p className="text-muted-foreground">
                        Track outreach progress for <span className="font-semibold text-foreground">{currentEvent.name}</span>
                    </p>
                </div>
                <Button size="sm" className="gap-1.5">
                    <Users className="h-4 w-4" />
                    New Contact
                </Button>
            </div>

            {/* Outreach Targets Section */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {currentEvent.targets && (
                    <>
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm font-medium text-muted-foreground flex justify-between">
                                    Judges Secured
                                    <Briefcase className="h-4 w-4 text-primary" />
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="flex items-end justify-between mb-2">
                                    <div className="text-3xl font-bold">
                                        {currentEvent.targets.judges.current}
                                        <span className="text-lg text-muted-foreground font-normal">/{currentEvent.targets.judges.target}</span>
                                    </div>
                                    <span className="text-xs text-muted-foreground">
                                        {Math.round((currentEvent.targets.judges.current / currentEvent.targets.judges.target) * 100)}% to goal
                                    </span>
                                </div>
                                <Progress value={(currentEvent.targets.judges.current / currentEvent.targets.judges.target) * 100} className="h-2" />
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm font-medium text-muted-foreground flex justify-between">
                                    Delegates Confirmed
                                    <Users className="h-4 w-4 text-purple-500" />
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="flex items-end justify-between mb-2">
                                    <div className="text-3xl font-bold">
                                        {currentEvent.targets.delegates.current}
                                        <span className="text-lg text-muted-foreground font-normal">/{currentEvent.targets.delegates.target}</span>
                                    </div>
                                    <span className="text-xs text-muted-foreground">
                                        {Math.round((currentEvent.targets.delegates.current / currentEvent.targets.delegates.target) * 100)}% to goal
                                    </span>
                                </div>
                                <Progress value={(currentEvent.targets.delegates.current / currentEvent.targets.delegates.target) * 100} className="h-2" />
                            </CardContent>
                        </Card>
                    </>
                )}
            </div>

            {/* Sponsor Status Table */}
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <h2 className="text-lg font-semibold">Sponsor Status</h2>
                    <div className="flex gap-2">
                        <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                            {signedCount} Signed
                        </Badge>
                        <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                            {agreedCount} Agreed
                        </Badge>
                        <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200">
                            {inTalksCount} In Talks
                        </Badge>
                        <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">
                            {rejectedCount} Rejected
                        </Badge>
                    </div>
                </div>

                <Card>
                    <CardContent className="p-0">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b bg-muted/30">
                                    <th className="text-left font-medium text-muted-foreground p-3 pl-4">Partner</th>
                                    <th className="text-left font-medium text-muted-foreground p-3">Category</th>
                                    <th className="text-left font-medium text-muted-foreground p-3">Status</th>
                                    <th className="text-left font-medium text-muted-foreground p-3">Amount</th>
                                    <th className="text-left font-medium text-muted-foreground p-3">Contact</th>
                                    <th className="p-3"></th>
                                </tr>
                            </thead>
                            <tbody>
                                {partners.length === 0 ? (
                                    <tr>
                                        <td colSpan={6} className="p-8 text-center text-muted-foreground">
                                            No partners found for this event.
                                        </td>
                                    </tr>
                                ) : (
                                    partners.map((partner) => (
                                        <tr key={partner.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                                            <td className="p-3 pl-4 font-medium">{partner.name}</td>
                                            <td className="p-3 capitalize text-muted-foreground">{partner.category}</td>
                                            <td className="p-3">
                                                <Badge variant="outline" className={getStatusStyle(partner.status)}>
                                                    {getStatusLabel(partner.status)}
                                                </Badge>
                                            </td>
                                            <td className="p-3 font-medium">
                                                {partner.amount > 0 ? `$${partner.amount.toLocaleString()}` : "—"}
                                            </td>
                                            <td className="p-3 text-muted-foreground">
                                                {partner.contactEmail}
                                            </td>
                                            <td className="p-3 text-right">
                                                <DropdownMenu>
                                                    <DropdownMenuTrigger asChild>
                                                        <Button variant="ghost" size="icon" className="h-8 w-8">
                                                            <MoreHorizontal className="h-4 w-4" />
                                                        </Button>
                                                    </DropdownMenuTrigger>
                                                    <DropdownMenuContent align="end">
                                                        <DropdownMenuItem>Edit Details</DropdownMenuItem>
                                                        <DropdownMenuItem>View Contract</DropdownMenuItem>
                                                        <Separator className="my-1" />
                                                        <DropdownMenuItem className="text-destructive">Remove</DropdownMenuItem>
                                                    </DropdownMenuContent>
                                                </DropdownMenu>
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </CardContent>
                </Card>
            </div>

            {/* Files & Timeline Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Files */}
                <div className="lg:col-span-2 space-y-4">
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        <FileText className="h-5 w-5 text-muted-foreground" />
                        Relevant Documents
                    </h2>
                    {currentEvent.files && currentEvent.files.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {currentEvent.files.map((file, idx) => (
                                <Card key={idx} className="hover:border-primary/50 cursor-pointer transition-colors group">
                                    <CardContent className="p-4 flex items-start gap-3">
                                        <div className={`p-2 rounded-md ${file.type === 'pdf' ? 'bg-red-50 text-red-600' :
                                            file.type === 'xlsx' ? 'bg-green-50 text-green-600' :
                                                file.type === 'gdoc' ? 'bg-blue-50 text-blue-600' :
                                                    'bg-gray-50 text-gray-600'
                                            }`}>
                                            <FileText className="h-5 w-5" />
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <p className="font-medium truncate group-hover:text-primary transition-colors">
                                                {file.name}
                                            </p>
                                            <p className="text-xs text-muted-foreground uppercase mt-0.5">
                                                {file.type}
                                            </p>
                                        </div>
                                        <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground">
                                            <Download className="h-4 w-4" />
                                        </Button>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    ) : (
                        <div className="p-8 border border-dashed rounded-lg text-center text-muted-foreground">
                            No files uploaded yet.
                        </div>
                    )}
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
