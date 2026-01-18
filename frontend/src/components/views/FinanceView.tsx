"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { DollarSign, TrendingUp, TrendingDown } from "lucide-react";

const EXPENSES = [
    { description: "Venue Deposit", category: "Logistics", amount: "$15,000", date: "Jan 15, 2026", status: "Paid" },
    { description: "Catering Downpayment", category: "Food & Bev", amount: "$5,000", date: "Jan 16, 2026", status: "Pending" },
    { description: "AWS Credits", category: "Infrastructure", amount: "$2,500", date: "Jan 10, 2026", status: "Paid" },
    { description: "Marketing Materials", category: "Marketing", amount: "$1,200", date: "Jan 12, 2026", status: "Paid" },
    { description: "Speaker Travel", category: "Logistics", amount: "$3,500", date: "Jan 18, 2026", status: "Pending" },
];

export function FinanceView() {
    return (
        <div className="max-w-5xl">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold tracking-tight text-slate-900">
                    Finance
                </h1>
                <p className="text-slate-500 mt-1">
                    Budget tracking and expense management.
                </p>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-4 gap-4 mb-8">
                <StatCard
                    label="Total Budget"
                    value="$250,000"
                    icon={DollarSign}
                />
                <StatCard
                    label="Spent to Date"
                    value="$84,320"
                    subtext="33.7% of budget"
                    icon={TrendingDown}
                    iconColor="text-red-500"
                />
                <StatCard
                    label="Remaining"
                    value="$165,680"
                    icon={TrendingUp}
                    iconColor="text-emerald-500"
                />
                <StatCard
                    label="Pending Invoices"
                    value="3"
                    subtext="$8,500 total"
                />
            </div>

            <Separator className="my-8" />

            {/* Expense Ledger */}
            <div>
                <h2 className="text-lg font-semibold text-slate-900 tracking-tight mb-4">
                    Expense Ledger
                </h2>

                <Card className="border border-slate-200 shadow-sm">
                    <Table>
                        <TableHeader>
                            <TableRow className="border-b border-slate-200 hover:bg-transparent">
                                <TableHead className="text-slate-500 font-medium">Description</TableHead>
                                <TableHead className="text-slate-500 font-medium">Category</TableHead>
                                <TableHead className="text-slate-500 font-medium">Amount</TableHead>
                                <TableHead className="text-slate-500 font-medium">Date</TableHead>
                                <TableHead className="text-slate-500 font-medium">Status</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {EXPENSES.map((expense, idx) => (
                                <TableRow
                                    key={idx}
                                    className="border-b border-slate-100 last:border-0 hover:bg-slate-50/50"
                                >
                                    <TableCell className="font-medium text-slate-900">{expense.description}</TableCell>
                                    <TableCell className="text-slate-500">{expense.category}</TableCell>
                                    <TableCell className="text-slate-700 font-mono">{expense.amount}</TableCell>
                                    <TableCell className="text-slate-500">{expense.date}</TableCell>
                                    <TableCell>
                                        <Badge
                                            variant="outline"
                                            className={expense.status === "Paid"
                                                ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                                                : "bg-amber-50 text-amber-700 border-amber-200"
                                            }
                                        >
                                            {expense.status}
                                        </Badge>
                                    </TableCell>
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
    icon: Icon,
    iconColor = "text-slate-400"
}: {
    label: string;
    value: string;
    subtext?: string;
    icon?: React.ElementType;
    iconColor?: string;
}) {
    return (
        <Card className="border border-slate-200 shadow-sm bg-white">
            <CardContent className="p-5">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-slate-500">{label}</span>
                    {Icon && <Icon className={`h-4 w-4 ${iconColor}`} />}
                </div>
                <div className="text-2xl font-semibold text-slate-900 tracking-tight">{value}</div>
                {subtext && <div className="text-xs text-slate-400 mt-1">{subtext}</div>}
            </CardContent>
        </Card>
    );
}
