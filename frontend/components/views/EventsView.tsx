"use client";

import React from "react";
import {
    Calendar,
    MapPin,
    Users,
    Plus,
    Search,
    Filter,
    MoreHorizontal
} from "lucide-react";
import { mockEvents } from "@/lib/config";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Separator } from "@/components/ui/separator";

export function EventsView() {
    return (
        <div className="space-y-8 animate-in fade-in duration-500 p-6 sm:p-8 max-w-[1600px] mx-auto">

            {/* Header Section */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-white">Events</h1>
                    <p className="text-muted-foreground mt-1">
                        Manage your global event portfolio and production status.
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <Button size="lg" className="gap-2 shadow-lg shadow-primary/20">
                        <Plus className="h-5 w-5" />
                        Create Event
                    </Button>
                </div>
            </div>

            {/* Stats Overview */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <StatsCard
                    title="Total Events"
                    value={mockEvents.length.toString()}
                    icon={<Calendar className="h-4 w-4 text-muted-foreground" />}
                    trend="+2 this month"
                />
                <StatsCard
                    title="Active Now"
                    value="3"
                    icon={<Users className="h-4 w-4 text-muted-foreground" />}
                    trend="85% capacity"
                />
                <StatsCard
                    title="Pending Approval"
                    value="1"
                    icon={<Filter className="h-4 w-4 text-muted-foreground" />}
                    trend="Action required"
                />
                <StatsCard
                    title="Total Revenue"
                    value="$2.4M"
                    icon={<MapPin className="h-4 w-4 text-muted-foreground" />}
                    trend="+12% vs last year"
                />
            </div>

            <Separator className="bg-slate-800" />

            {/* Filters & Toolbar */}
            <div className="flex flex-col sm:flex-row justify-between gap-4 items-center bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                <div className="relative w-full sm:w-96">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                    <Input
                        placeholder="Search events..."
                        className="pl-10 bg-slate-950 border-slate-800 focus-visible:ring-primary text-slate-200"
                    />
                </div>
                <div className="flex gap-2 w-full sm:w-auto">
                    <Button variant="outline" className="gap-2 border-slate-800 hover:bg-slate-800 text-slate-300">
                        <Filter className="h-4 w-4" />
                        Filter
                    </Button>
                    <Button variant="outline" className="gap-2 border-slate-800 hover:bg-slate-800 text-slate-300">
                        Sort by
                    </Button>
                </div>
            </div>

            {/* Events Grid */}
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3">
                {mockEvents.map((event) => (
                    <Card key={event.id} className="bg-slate-900 border-slate-800 hover:border-slate-700 transition-all hover:shadow-xl hover:shadow-primary/5 group">
                        <CardHeader className="pb-3">
                            <div className="flex justify-between items-start">
                                <Badge
                                    variant={event.status === 'active' ? 'default' : 'secondary'}
                                    className={
                                        event.status === 'active' ? 'bg-emerald-500/15 text-emerald-400 hover:bg-emerald-500/25 border-emerald-500/20' :
                                            event.status === 'planning' ? 'bg-blue-500/15 text-blue-400 hover:bg-blue-500/25 border-blue-500/20' :
                                                'bg-slate-700 text-slate-300'
                                    }
                                >
                                    {event.status.charAt(0).toUpperCase() + event.status.slice(1)}
                                </Badge>
                                <DropdownMenu>
                                    <DropdownMenuTrigger asChild>
                                        <Button variant="ghost" size="icon" className="h-8 w-8 text-slate-400 hover:text-white -mr-3">
                                            <MoreHorizontal className="h-4 w-4" />
                                        </Button>
                                    </DropdownMenuTrigger>
                                    <DropdownMenuContent align="end" className="bg-slate-900 border-slate-800 text-slate-300">
                                        <DropdownMenuItem className="hover:bg-slate-800 cursor-pointer">View Details</DropdownMenuItem>
                                        <DropdownMenuItem className="hover:bg-slate-800 cursor-pointer">Edit Settings</DropdownMenuItem>
                                        <Separator className="bg-slate-800 my-1" />
                                        <DropdownMenuItem className="text-red-400 hover:bg-red-950/30 hover:text-red-300 cursor-pointer">Archive</DropdownMenuItem>
                                    </DropdownMenuContent>
                                </DropdownMenu>
                            </div>
                            <CardTitle className="text-xl font-bold text-white group-hover:text-primary transition-colors mt-2 truncate">
                                {event.name}
                            </CardTitle>
                            <CardDescription className="flex items-center gap-2 mt-1">
                                <MapPin className="h-3.5 w-3.5" />
                                {event.location}
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="pb-3">
                            <div className="space-y-3">
                                <div className="flex items-center justify-between text-sm">
                                    <span className="text-muted-foreground flex items-center gap-2">
                                        <Calendar className="h-3.5 w-3.5" />
                                        Date
                                    </span>
                                    <span className="text-slate-200">{new Date(event.date).toLocaleDateString()}</span>
                                </div>
                                <div className="flex items-center justify-between text-sm">
                                    <span className="text-muted-foreground flex items-center gap-2">
                                        <Users className="h-3.5 w-3.5" />
                                        Attendees
                                    </span>
                                    <span className="text-slate-200">{event.attendees.toLocaleString()}</span>
                                </div>
                            </div>

                            {/* Progress / Agent Status Placeholder */}
                            <div className="mt-4 p-3 bg-slate-950/50 rounded-lg border border-slate-800/50">
                                <div className="flex items-center justify-between text-xs mb-2">
                                    <span className="text-slate-400">Agent Activity</span>
                                    <span className="text-emerald-400">Active</span>
                                </div>
                                <div className="flex gap-1">
                                    <div className="h-1 flex-1 bg-emerald-500 rounded-full animate-pulse"></div>
                                    <div className="h-1 flex-1 bg-blue-500 rounded-full"></div>
                                    <div className="h-1 flex-1 bg-slate-800 rounded-full"></div>
                                </div>
                            </div>
                        </CardContent>
                        <CardFooter className="pt-2">
                            <Button className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700/50">
                                Open Dashboard
                            </Button>
                        </CardFooter>
                    </Card>
                ))}

                {/* Add New Card Stub */}
                <Button variant="ghost" className="h-auto min-h-[300px] border-2 border-dashed border-slate-800 rounded-xl hover:border-slate-700 hover:bg-slate-900/50 flex flex-col gap-4 text-slate-400 hover:text-white transition-all">
                    <div className="h-14 w-14 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center">
                        <Plus className="h-7 w-7" />
                    </div>
                    <span className="font-semibold text-lg">Create New Event</span>
                </Button>
            </div>
        </div>
    );
}

function StatsCard({ title, value, icon, trend }: { title: string, value: string, icon: React.ReactNode, trend: string }) {
    return (
        <Card className="bg-slate-900 border-slate-800 p-1">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-slate-400">
                    {title}
                </CardTitle>
                {icon}
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold text-white">{value}</div>
                <p className="text-xs text-muted-foreground mt-1">
                    {trend}
                </p>
            </CardContent>
        </Card>
    )
}
