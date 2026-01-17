"use client";

interface FinanceViewProps {
    // Add props as needed in Phase 2
}

/**
 * Finance view - displays financial stats and MOUs.
 * Skeleton to be fully implemented in Phase 2.
 */
export function FinanceView({ }: FinanceViewProps): React.ReactElement {
    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-primary">Finance</h1>
            </div>

            {/* Stats Grid Placeholder */}
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                {/* Budget */}
                <div className="p-6 bg-white rounded-lg shadow-sm border border-slate-200">
                    <p className="text-sm text-slate-500 mb-1">Total Budget</p>
                    <div className="h-8 w-24 bg-slate-200 rounded animate-pulse"></div>
                </div>

                {/* Spent */}
                <div className="p-6 bg-white rounded-lg shadow-sm border border-slate-200">
                    <p className="text-sm text-slate-500 mb-1">Spent</p>
                    <div className="h-8 w-20 bg-slate-200 rounded animate-pulse"></div>
                </div>

                {/* MOUs */}
                <div className="p-6 bg-white rounded-lg shadow-sm border border-slate-200">
                    <p className="text-sm text-slate-500 mb-1">Active MOUs</p>
                    <div className="h-8 w-12 bg-slate-200 rounded animate-pulse"></div>
                </div>

                {/* Pending */}
                <div className="p-6 bg-white rounded-lg shadow-sm border border-slate-200">
                    <p className="text-sm text-slate-500 mb-1">Pending Approvals</p>
                    <div className="h-8 w-12 bg-slate-200 rounded animate-pulse"></div>
                </div>
            </div>

            {/* Skeleton message */}
            <p className="text-center text-slate-400 text-sm mt-8">
                Finance view skeleton - to be implemented in Phase 2
            </p>
        </div>
    );
}
