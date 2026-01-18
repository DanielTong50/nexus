"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Calendar } from "lucide-react";

const SCHEDULED_POSTS = [
    { platform: "Instagram", title: "Speaker Announcement", date: "Today, 2:00 PM", status: "Scheduled" },
    { platform: "Twitter", title: "Ticket Sale Reminder", date: "Tomorrow, 10:00 AM", status: "Draft" },
    { platform: "LinkedIn", title: "Sponsor Spotlight: Google", date: "Jan 20, 9:00 AM", status: "Approved" },
];

const ASSETS = [
    { name: "Event Banner v2", type: "Image", size: "1920x1080" },
    { name: "Instagram Story Template", type: "Template", size: "1080x1920" },
    { name: "Sponsor Deck 2026", type: "PDF", size: "24 pages" },
    { name: "Logo Pack", type: "Archive", size: "12 files" },
];

export function MarketingView() {
    return (
        <div className="max-w-5xl">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold tracking-tight text-slate-900">
                    Marketing
                </h1>
                <p className="text-slate-500 mt-1">
                    Campaigns, content calendar, and brand assets.
                </p>
            </div>

            <Tabs defaultValue="calendar" className="w-full">
                <TabsList className="bg-slate-100 p-1 h-10">
                    <TabsTrigger value="calendar" className="text-sm">Content Calendar</TabsTrigger>
                    <TabsTrigger value="assets" className="text-sm">Brand Assets</TabsTrigger>
                </TabsList>

                <TabsContent value="calendar" className="mt-6">
                    <div className="flex items-center gap-2 mb-4">
                        <Calendar className="h-4 w-4 text-slate-400" />
                        <h2 className="text-lg font-semibold text-slate-900 tracking-tight">
                            Upcoming Posts
                        </h2>
                    </div>

                    <Card className="border border-slate-200 shadow-sm">
                        <CardContent className="p-0">
                            {SCHEDULED_POSTS.map((post, idx) => (
                                <div
                                    key={idx}
                                    className="flex items-center gap-4 px-5 py-4 border-b border-slate-100 last:border-0 hover:bg-slate-50/50 cursor-pointer"
                                >
                                    <div className="flex-1">
                                        <div className="text-xs text-slate-400 uppercase font-medium mb-1">
                                            {post.platform}
                                        </div>
                                        <div className="text-sm text-slate-900 font-medium">
                                            {post.title}
                                        </div>
                                    </div>
                                    <div className="text-sm text-slate-500">
                                        {post.date}
                                    </div>
                                    <StatusBadge status={post.status} />
                                </div>
                            ))}
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="assets" className="mt-6">
                    <h2 className="text-lg font-semibold text-slate-900 tracking-tight mb-4">
                        Brand Assets
                    </h2>

                    <div className="grid grid-cols-4 gap-4">
                        {ASSETS.map((asset, idx) => (
                            <Card key={idx} className="border border-slate-200 shadow-sm hover:border-slate-300 cursor-pointer transition-colors">
                                <CardContent className="p-4">
                                    <div className="h-20 bg-slate-100 rounded mb-3 flex items-center justify-center text-slate-400 text-xs">
                                        Preview
                                    </div>
                                    <div className="text-sm font-medium text-slate-900 truncate">{asset.name}</div>
                                    <div className="text-xs text-slate-400">{asset.type} • {asset.size}</div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
}

function StatusBadge({ status }: { status: string }) {
    const styles: Record<string, string> = {
        Scheduled: "bg-blue-50 text-blue-700 border-blue-200",
        Draft: "bg-slate-50 text-slate-600 border-slate-200",
        Approved: "bg-emerald-50 text-emerald-700 border-emerald-200",
    };

    return (
        <Badge variant="outline" className={`font-normal text-xs ${styles[status]}`}>
            {status}
        </Badge>
    );
}
