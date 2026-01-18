"use client";

import React from "react";
import {
    GitBranch,
    Star,
    Lock,
    Unlock,
    Zap,
    Box,
    Wrench,
    Calendar,
    Code,
    ExternalLink
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
    CardDescription
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";

export function DevelopersView() {
    const { eventId } = useEvent();
    const currentEvent = mockEvents.find(e => e.id === eventId);

    if (!currentEvent) return null;

    // Helper for update icons and colors
    const getUpdateIcon = (type: string) => {
        switch (type) {
            case 'feature': return <Zap className="h-4 w-4 text-yellow-500" />;
            case 'fix': return <Wrench className="h-4 w-4 text-red-500" />;
            case 'component': return <Box className="h-4 w-4 text-blue-500" />;
            default: return <Code className="h-4 w-4 text-gray-500" />;
        }
    };

    const getUpdateColor = (type: string) => {
        switch (type) {
            case 'feature': return "bg-yellow-50 border-yellow-100";
            case 'fix': return "bg-red-50 border-red-100";
            case 'component': return "bg-blue-50 border-blue-100";
            default: return "bg-gray-50 border-gray-100";
        }
    };

    return (
        <div className="flex-1 p-6 space-y-8 max-w-[1600px] mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Developer Portal</h1>
                    <p className="text-muted-foreground">
                        Technical updates and repository management for <span className="font-semibold text-foreground">{currentEvent.name}</span>
                    </p>
                </div>
                <Button size="sm" className="gap-1.5">
                    <GitBranch className="h-4 w-4" />
                    New Pull Request
                </Button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Development Updates Feed */}
                <div className="lg:col-span-2 space-y-4">
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        <Zap className="h-5 w-5 text-muted-foreground" />
                        Fresh Updates
                    </h2>

                    {currentEvent.devUpdates && currentEvent.devUpdates.length > 0 ? (
                        <div className="space-y-4">
                            {currentEvent.devUpdates.map((update, idx) => (
                                <Card key={idx} className="transition-all hover:bg-muted/10">
                                    <CardContent className="p-4 flex gap-4">
                                        <div className={`mt-1 p-2 rounded-full h-8 w-8 flex items-center justify-center border ${getUpdateColor(update.type)}`}>
                                            {getUpdateIcon(update.type)}
                                        </div>
                                        <div className="flex-1 space-y-1">
                                            <div className="flex items-center justify-between">
                                                <h3 className="font-semibold text-sm">{update.title}</h3>
                                                <span className="text-xs text-muted-foreground">
                                                    {new Date(update.date).toLocaleDateString()}
                                                </span>
                                            </div>
                                            <p className="text-sm text-muted-foreground leading-relaxed">
                                                {update.description}
                                            </p>
                                            <div className="flex items-center gap-2 pt-2">
                                                <Badge variant="outline" className="text-[10px] font-normal capitalize">
                                                    {update.type}
                                                </Badge>
                                                <span className="text-xs text-muted-foreground flex items-center gap-1">
                                                    by <span className="font-medium text-foreground">{update.author}</span>
                                                </span>
                                            </div>
                                        </div>
                                    </CardContent>
                                </Card>
                            ))}
                        </div>
                    ) : (
                        <div className="p-12 border-2 border-dashed rounded-xl text-center text-muted-foreground">
                            No recent updates posted.
                        </div>
                    )}
                </div>

                {/* Right Column: Sprint Roadmap */}
                <div className="space-y-4">
                    <h2 className="text-lg font-semibold flex items-center gap-2">
                        <Calendar className="h-5 w-5 text-muted-foreground" />
                        Sprint Roadmap
                    </h2>
                    <Card>
                        <CardContent className="p-0">
                            <div className="divide-y">
                                {currentEvent.timeline?.map((item, idx) => (
                                    <div key={idx} className="p-4 flex gap-4 hover:bg-muted/20 transition-colors group">
                                        <div className="flex flex-col items-center min-w-[3rem]">
                                            <span className="text-xs text-muted-foreground font-medium uppercase">
                                                {new Date(item.date).toLocaleDateString('en-US', { month: 'short' })}
                                            </span>
                                            <span className="text-lg font-bold group-hover:text-primary transition-colors">
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
                                        No roadmap items found.
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>

            <Separator />

            {/* Repositories Grid */}
            <div className="space-y-4">
                <h2 className="text-lg font-semibold flex items-center gap-2">
                    <Code className="h-5 w-5 text-muted-foreground" />
                    Repositories
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {currentEvent.githubRepos && currentEvent.githubRepos.length > 0 ? (
                        currentEvent.githubRepos.map((repo, idx) => (
                            <Card key={idx} className="hover:border-primary/50 cursor-pointer transition-colors group">
                                <CardHeader className="p-4 pb-2">
                                    <div className="flex items-start justify-between">
                                        <div className="flex items-center gap-2">
                                            <Box className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
                                            <CardTitle className="text-base font-semibold">{repo.name}</CardTitle>
                                        </div>
                                        {repo.status === 'private' ? (
                                            <Badge variant="secondary" className="bg-yellow-50 text-yellow-700 hover:bg-yellow-100 border-yellow-200 gap-1 text-[10px]">
                                                <Lock className="h-3 w-3" /> Private
                                            </Badge>
                                        ) : (
                                            <Badge variant="secondary" className="bg-green-50 text-green-700 hover:bg-green-100 border-green-200 gap-1 text-[10px]">
                                                <Unlock className="h-3 w-3" /> Public
                                            </Badge>
                                        )}
                                    </div>
                                </CardHeader>
                                <CardContent className="p-4 pt-1">
                                    <div className="flex items-center justify-between text-sm text-muted-foreground mt-2">
                                        <div className="flex items-center gap-4">
                                            <div className="flex items-center gap-1">
                                                <Star className="h-4 w-4 text-amber-400 fill-amber-400" />
                                                <span className="font-medium text-foreground">{repo.stars}</span>
                                            </div>
                                            <div className="flex items-center gap-1 text-xs">
                                                <div className="h-2 w-2 rounded-full bg-blue-500" />
                                                TypeScript
                                            </div>
                                        </div>
                                        <ExternalLink className="h-4 w-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                                    </div>
                                </CardContent>
                            </Card>
                        ))
                    ) : (
                        <div className="col-span-full p-8 border border-dashed rounded-lg text-center text-muted-foreground">
                            No repositories linked.
                        </div>
                    )}
                </div>
            </div>

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
