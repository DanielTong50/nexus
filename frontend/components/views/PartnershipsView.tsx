"use client";

interface PartnershipsViewProps {
    // Add props as needed in Phase 2
}

/**
 * Partnerships view - displays stats like money raised, judges count.
 * Skeleton to be fully implemented in Phase 2.
 */
export function PartnershipsView({ }: PartnershipsViewProps): React.ReactElement {
    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-primary">Partnerships</h1>
            </div>

            {/* Stats Grid Placeholder */}
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
                {/* Money Raised */}
                <div className="p-6 bg-white rounded-lg shadow-sm border border-slate-200">
                    <p className="text-sm text-slate-500 mb-1">Money Raised</p>
                    <div className="h-8 w-24 bg-slate-200 rounded animate-pulse"></div>
                </div>

                {/* Sponsors */}
                <div className="p-6 bg-white rounded-lg shadow-sm border border-slate-200">
                    <p className="text-sm text-slate-500 mb-1">Sponsors</p>
                    <div className="h-8 w-16 bg-slate-200 rounded animate-pulse"></div>
                </div>

                {/* Judges */}
                <div className="p-6 bg-white rounded-lg shadow-sm border border-slate-200">
                    <p className="text-sm text-slate-500 mb-1">Judges</p>
                    <div className="h-8 w-16 bg-slate-200 rounded animate-pulse"></div>
                </div>

                {/* Pending */}
                <div className="p-6 bg-white rounded-lg shadow-sm border border-slate-200">
                    <p className="text-sm text-slate-500 mb-1">Pending Outreach</p>
                    <div className="h-8 w-16 bg-slate-200 rounded animate-pulse"></div>
                </div>
            </div>

            {/* Skeleton message */}
            <p className="text-center text-slate-400 text-sm mt-8">
                Partnerships view skeleton - stats display with event filter coming in Phase 2
            </p>
        </div>
    );
}
