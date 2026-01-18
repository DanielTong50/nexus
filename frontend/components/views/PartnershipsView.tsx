"use client";

import React from "react";
import {
    Search,
    Plus,
    MoreHorizontal,
} from "lucide-react";
import { mockPartners, mockEvents, type Partner } from "@/lib/config";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
import { Separator } from "@/components/ui/separator";

export function PartnershipsView() {
    const totalRaised = mockPartners
        .filter((p) => p.status === "confirmed")
        .reduce((sum, p) => sum + p.amount, 0);
    const pendingAmount = mockPartners
        .filter((p) => p.status === "pending" || p.status === "negotiating")
        .reduce((sum, p) => sum + p.amount, 0);
    const confirmedCount = mockPartners.filter((p) => p.status === "confirmed").length;
    const judgesCount = mockPartners.filter((p) => p.category === "judge").length;

    const getStatusStyle = (status: Partner["status"]) => {
        switch (status) {
            case "confirmed": return "bg-green-50 text-green-700 border-green-200";
            case "pending": return "bg-yellow-50 text-yellow-700 border-yellow-200";
            case "negotiating": return "bg-blue-50 text-blue-700 border-blue-200";
            case "declined": return "bg-red-50 text-red-700 border-red-200";
            default: return "";
        }
    };

    return (
        <div className="flex-1 p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-xl font-semibold">Partnerships</h1>
                    <p className="text-sm text-muted-foreground">Manage sponsors, judges, and mentors</p>
                </div>
                <Button size="sm" className="gap-1.5">
                    <Plus className="h-4 w-4" />
                    Add Partner
                </Button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-4 gap-4">
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">Total Raised</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-semibold">${totalRaised.toLocaleString()}</div>
                        <p className="text-xs text-green-600 mt-1">+12% from last event</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">Pending</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-semibold">${pendingAmount.toLocaleString()}</div>
                        <p className="text-xs text-muted-foreground mt-1">3 in negotiation</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">Confirmed</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-semibold">{confirmedCount}</div>
                        <p className="text-xs text-muted-foreground mt-1">partners</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-muted-foreground">Judges</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-semibold">{judgesCount}</div>
                        <p className="text-xs text-yellow-600 mt-1">2 more needed</p>
                    </CardContent>
                </Card>
            </div>

            {/* Search */}
            <div className="flex gap-3">
                <div className="relative flex-1 max-w-xs">
                    <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input placeholder="Search..." className="pl-8 h-9" />
                </div>
                <Button variant="outline" size="sm">All Events</Button>
                <Button variant="outline" size="sm">All Status</Button>
            </div>

            {/* Table */}
            <Card>
                <CardContent className="p-0">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b">
                                <th className="text-left font-medium text-muted-foreground p-3">Partner</th>
                                <th className="text-left font-medium text-muted-foreground p-3">Category</th>
                                <th className="text-left font-medium text-muted-foreground p-3">Status</th>
                                <th className="text-left font-medium text-muted-foreground p-3">Amount</th>
                                <th className="text-left font-medium text-muted-foreground p-3">Contact</th>
                                <th className="p-3"></th>
                            </tr>
                        </thead>
                        <tbody>
                            {mockPartners.map((partner) => {
                                const event = mockEvents.find((e) => e.id === partner.eventId);
                                return (
                                    <tr key={partner.id} className="border-b last:border-0 hover:bg-muted/30">
                                        <td className="p-3">
                                            <div className="flex items-center gap-2.5">
                                                <div className="h-7 w-7 rounded-full bg-muted flex items-center justify-center text-xs font-medium">
                                                    {partner.name.charAt(0)}
                                                </div>
                                                <div>
                                                    <div className="font-medium">{partner.name}</div>
                                                    <div className="text-xs text-muted-foreground">{event?.name}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="p-3 capitalize text-muted-foreground">{partner.category}</td>
                                        <td className="p-3">
                                            <Badge variant="outline" className={getStatusStyle(partner.status)}>
                                                {partner.status}
                                            </Badge>
                                        </td>
                                        <td className="p-3 font-medium">
                                            {partner.amount > 0 ? `$${partner.amount.toLocaleString()}` : "—"}
                                        </td>
                                        <td className="p-3">
                                            <div className="text-xs">
                                                <div>{partner.contactName}</div>
                                                <div className="text-muted-foreground">{partner.contactEmail}</div>
                                            </div>
                                        </td>
                                        <td className="p-3">
                                            <DropdownMenu>
                                                <DropdownMenuTrigger asChild>
                                                    <Button variant="ghost" size="icon" className="h-7 w-7">
                                                        <MoreHorizontal className="h-4 w-4" />
                                                    </Button>
                                                </DropdownMenuTrigger>
                                                <DropdownMenuContent align="end">
                                                    <DropdownMenuItem>View</DropdownMenuItem>
                                                    <DropdownMenuItem>Edit</DropdownMenuItem>
                                                    <Separator className="my-1" />
                                                    <DropdownMenuItem className="text-destructive">Remove</DropdownMenuItem>
                                                </DropdownMenuContent>
                                            </DropdownMenu>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </CardContent>
            </Card>
        </div>
    );
}
