"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Plus, ArrowUpRight, TrendingUp } from "lucide-react";

const SPONSORS = [
    { name: "Google", tier: "Platinum", amount: "$25,000", status: "Confirmed", contact: "Sarah Chen" },
    { name: "Microsoft", tier: "Gold", amount: "$15,000", status: "Confirmed", contact: "Mike Ross" },
    { name: "Stripe", tier: "Gold", amount: "$15,000", status: "Pending", contact: "Alex Kumar" },
    { name: "Vercel", tier: "Silver", amount: "$5,000", status: "In Discussion", contact: "Lee Robinson" },
    { name: "MongoDB", tier: "Silver", amount: "$5,000", status: "Confirmed", contact: "Dev Ittycheria" },
];

export function PartnershipsView() {
    return (
        <div className="max-w-5xl">
            {/* Header */}
            <div className="flex items-start justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-slate-900">
                        Partnerships
                    </h1>
                    <p className="text-slate-500 mt-1">
                        Manage sponsors, speakers, and strategic partners.
                    </p>
                </div>
                <Button className="bg-slate-900 hover:bg-slate-800 text-white gap-2" size="sm">
                    <Plus className="h-4 w-4" />
                    Add Partner
                </Button>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-4 gap-4 mb-8">
                <StatCard
                    label="Total Raised"
                    value="$65,000"
                    subtext="+$15k this week"
                    trend="up"
                />
                <StatCard
                    label="Goal Progress"
                    value="65%"
                    subtext="of $100k target"
                />
                <StatCard
                    label="Active Partners"
                    value="5"
                    subtext="3 pending outreach"
                />
                <StatCard
                    label="Avg. Deal Size"
                    value="$13,000"
                    subtext="+23% vs. last year"
                    trend="up"
                />
            </div>

            <Separator className="my-8" />

            {/* Sponsors Table */}
            <div>
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold text-slate-900 tracking-tight">
                        Sponsor Pipeline
                    </h2>
                    <Button variant="outline" size="sm" className="text-slate-500 gap-2">
                        Export
                        <ArrowUpRight className="h-3 w-3" />
                    </Button>
                </div>

                <Card className="border border-slate-200 shadow-sm">
                    <Table>
                        <TableHeader>
                            <TableRow className="border-b border-slate-200 hover:bg-transparent">
                                <TableHead className="text-slate-500 font-medium">Company</TableHead>
                                <TableHead className="text-slate-500 font-medium">Tier</TableHead>
                                <TableHead className="text-slate-500 font-medium">Amount</TableHead>
                                <TableHead className="text-slate-500 font-medium">Status</TableHead>
                                <TableHead className="text-slate-500 font-medium">Contact</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {SPONSORS.map((sponsor) => (
                                <TableRow
                                    key={sponsor.name}
                                    className="border-b border-slate-100 last:border-0 hover:bg-slate-50/50 cursor-pointer"
                                >
                                    <TableCell className="font-medium text-slate-900">{sponsor.name}</TableCell>
                                    <TableCell>
                                        <Badge variant="outline" className="font-normal">
                                            {sponsor.tier}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="text-slate-700">{sponsor.amount}</TableCell>
                                    <TableCell>
                                        <StatusBadge status={sponsor.status} />
                                    </TableCell>
                                    <TableCell className="text-slate-500">{sponsor.contact}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </Card>
            </div>
        </div>
    );
}

function StatCard({
    label,
    value,
    subtext,
    trend
}: {
    label: string;
    value: string;
    subtext: string;
    trend?: "up" | "down";
}) {
    return (
        <Card className="border border-slate-200 shadow-sm bg-white">
            <CardContent className="p-5">
                <div className="text-sm text-slate-500 mb-1">{label}</div>
                <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-semibold text-slate-900 tracking-tight">{value}</span>
                    {trend === "up" && <TrendingUp className="h-4 w-4 text-emerald-500" />}
                </div>
                <div className="text-xs text-slate-400 mt-1">{subtext}</div>
            </CardContent>
        </Card>
    );
}

function StatusBadge({ status }: { status: string }) {
    const styles: Record<string, string> = {
        "Confirmed": "bg-emerald-50 text-emerald-700 border-emerald-200",
        "Pending": "bg-amber-50 text-amber-700 border-amber-200",
        "In Discussion": "bg-slate-50 text-slate-600 border-slate-200",
    };

    return (
        <Badge
            variant="outline"
            className={`font-normal ${styles[status] || styles["In Discussion"]}`}
        >
            {status}
        </Badge>
    );
}
