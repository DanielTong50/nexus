"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Plus, Clock } from "lucide-react";

const SCHEDULE = [
    { time: "08:00 AM", event: "Registration & Breakfast", status: "completed" },
    { time: "09:30 AM", event: "Opening Ceremony", status: "completed" },
    { time: "10:00 AM", event: "Hacking Begins", status: "active" },
    { time: "12:30 PM", event: "Lunch Service", status: "upcoming" },
    { time: "03:00 PM", event: "Workshop: Intro to AI", status: "upcoming" },
    { time: "06:00 PM", event: "Dinner", status: "upcoming" },
];

const TASKS = [
    { label: "Confirm WiFi Bandwidth", done: true },
    { label: "Power Strips Distributed", done: true },
    { label: "Security Guard Briefing", done: false },
    { label: "Judge Room Setup", done: false },
    { label: "Swag Bags Packed", done: false },
];

export function EventsView() {
    return (
        <div className="max-w-5xl">
            {/* Header */}
            <div className="flex items-start justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-slate-900">
                        Events
                    </h1>
                    <p className="text-slate-500 mt-1">
                        Logistics, schedule, and run of show.
                    </p>
                </div>
                <Button className="bg-slate-900 hover:bg-slate-800 text-white gap-2" size="sm">
                    <Plus className="h-4 w-4" />
                    Add Event
                </Button>
            </div>

            <div className="grid grid-cols-3 gap-6">
                {/* Schedule */}
                <div className="col-span-2">
                    <div className="flex items-center gap-2 mb-4">
                        <Clock className="h-4 w-4 text-slate-400" />
                        <h2 className="text-lg font-semibold text-slate-900 tracking-tight">
                            Run of Show (Day 1)
                        </h2>
                    </div>

                    <Card className="border border-slate-200 shadow-sm">
                        <CardContent className="p-0">
                            {SCHEDULE.map((item, idx) => (
                                <div
                                    key={idx}
                                    className="flex items-center gap-4 px-5 py-4 border-b border-slate-100 last:border-0"
                                >
                                    <span className="text-sm text-slate-400 w-20 font-mono">{item.time}</span>
                                    <span className="text-sm text-slate-900 flex-1">{item.event}</span>
                                    <StatusBadge status={item.status} />
                                </div>
                            ))}
                        </CardContent>
                    </Card>
                </div>

                {/* Tasks */}
                <div>
                    <h2 className="text-lg font-semibold text-slate-900 tracking-tight mb-4">
                        Venue Logistics
                    </h2>

                    <Card className="border border-slate-200 shadow-sm">
                        <CardContent className="p-4 space-y-3">
                            {TASKS.map((task, idx) => (
                                <div key={idx} className="flex items-center gap-3">
                                    <Checkbox
                                        checked={task.done}
                                        className="border-slate-300 data-[state=checked]:bg-slate-900 data-[state=checked]:border-slate-900"
                                    />
                                    <span className={`text-sm ${task.done ? 'text-slate-400 line-through' : 'text-slate-700'}`}>
                                        {task.label}
                                    </span>
                                </div>
                            ))}
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}

function StatusBadge({ status }: { status: string }) {
    const styles: Record<string, string> = {
        completed: "bg-emerald-50 text-emerald-700 border-emerald-200",
        active: "bg-blue-50 text-blue-700 border-blue-200",
        upcoming: "bg-slate-50 text-slate-500 border-slate-200",
    };

    return (
        <Badge variant="outline" className={`font-normal text-xs ${styles[status]}`}>
            {status}
        </Badge>
    );
}
