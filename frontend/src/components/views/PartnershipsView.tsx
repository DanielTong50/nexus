"use client";

import {
    ArrowUpRight,
    CheckCircle,
    Circle,
    Clock,
} from "lucide-react";

const SPONSORS = [
    { name: "Google", tier: "Platinum", amount: "$25,000", status: "confirmed", contact: "Sarah Chen" },
    { name: "Microsoft", tier: "Gold", amount: "$15,000", status: "confirmed", contact: "Mike Ross" },
    { name: "Stripe", tier: "Gold", amount: "$15,000", status: "pending", contact: "Alex Kumar" },
    { name: "Vercel", tier: "Silver", amount: "$5,000", status: "discussion", contact: "Lee Robinson" },
    { name: "MongoDB", tier: "Silver", amount: "$5,000", status: "confirmed", contact: "Dev Ittycheria" },
];

const STATS = [
    { label: "Total Raised", value: "$65,000", subtext: "+$15k this week", trend: true },
    { label: "Goal Progress", value: "65%", subtext: "of $100k target", trend: false },
    { label: "Active Partners", value: "5", subtext: "3 pending outreach", trend: false },
    { label: "Avg. Deal Size", value: "$13,000", subtext: "+23% vs. last year", trend: true },
];

export function PartnershipsView() {
    return (
        <div className="max-w-5xl space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-semibold text-gray-900">Partnerships</h1>
                <p className="text-sm text-gray-500 mt-1">
                    Manage sponsors, speakers, and strategic partners.
                </p>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-4 gap-4">
                {STATS.map((stat) => (
                    <div key={stat.label} className="bg-white border border-gray-200 rounded-lg p-4">
                        <div className="text-xs text-gray-500 mb-1">{stat.label}</div>
                        <div className="flex items-baseline gap-2">
                            <span className="text-2xl font-semibold text-gray-900">{stat.value}</span>
                            {stat.trend && <ArrowUpRight className="h-4 w-4 text-green-600" />}
                        </div>
                        <div className="text-xs text-gray-400 mt-1">{stat.subtext}</div>
                    </div>
                ))}
            </div>

            {/* Table */}
            <div className="bg-white border border-gray-200 rounded-lg">
                <div className="px-4 py-3 border-b border-gray-200">
                    <span className="text-sm font-medium text-gray-900">Sponsor Pipeline</span>
                </div>
                <table className="w-full text-sm">
                    <thead>
                        <tr className="border-b border-gray-100 bg-gray-50">
                            <th className="text-left py-2 px-4 font-medium text-gray-500 text-xs">Company</th>
                            <th className="text-left py-2 px-4 font-medium text-gray-500 text-xs">Tier</th>
                            <th className="text-left py-2 px-4 font-medium text-gray-500 text-xs">Amount</th>
                            <th className="text-left py-2 px-4 font-medium text-gray-500 text-xs">Status</th>
                            <th className="text-left py-2 px-4 font-medium text-gray-500 text-xs">Contact</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {SPONSORS.map((sponsor) => (
                            <tr key={sponsor.name} className="hover:bg-gray-50">
                                <td className="py-2.5 px-4 font-medium text-gray-900">{sponsor.name}</td>
                                <td className="py-2.5 px-4">
                                    <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">
                                        {sponsor.tier}
                                    </span>
                                </td>
                                <td className="py-2.5 px-4 font-mono text-gray-700">{sponsor.amount}</td>
                                <td className="py-2.5 px-4">
                                    <StatusIndicator status={sponsor.status} />
                                </td>
                                <td className="py-2.5 px-4 text-gray-500">{sponsor.contact}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

function StatusIndicator({ status }: { status: string }) {
    if (status === "confirmed") {
        return (
            <span className="flex items-center gap-1.5 text-xs text-green-600">
                <CheckCircle className="h-3 w-3" />
                Confirmed
            </span>
        );
    }
    if (status === "pending") {
        return (
            <span className="flex items-center gap-1.5 text-xs text-amber-600">
                <Clock className="h-3 w-3" />
                Pending
            </span>
        );
    }
    return (
        <span className="flex items-center gap-1.5 text-xs text-gray-500">
            <Circle className="h-3 w-3" />
            In Discussion
        </span>
    );
}
