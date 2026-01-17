"use client";

interface MarketingViewProps {
    // Add props as needed in Phase 2
}

/**
 * Marketing view - displays marketing stats and content.
 * Skeleton to be fully implemented in Phase 2.
 */
export function MarketingView({ }: MarketingViewProps): React.ReactElement {
    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-primary">Marketing</h1>
            </div>

            {/* Stats Grid Placeholder */}
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {/* Social Posts */}
                <div className="p-6 bg-white rounded-lg shadow-sm border border-slate-200">
                    <p className="text-sm text-slate-500 mb-1">Social Posts</p>
                    <div className="h-8 w-16 bg-slate-200 rounded animate-pulse"></div>
                </div>

                {/* Email Campaigns */}
                <div className="p-6 bg-white rounded-lg shadow-sm border border-slate-200">
                    <p className="text-sm text-slate-500 mb-1">Email Campaigns</p>
                    <div className="h-8 w-16 bg-slate-200 rounded animate-pulse"></div>
                </div>

                {/* Reach */}
                <div className="p-6 bg-white rounded-lg shadow-sm border border-slate-200">
                    <p className="text-sm text-slate-500 mb-1">Total Reach</p>
                    <div className="h-8 w-24 bg-slate-200 rounded animate-pulse"></div>
                </div>
            </div>

            {/* Skeleton message */}
            <p className="text-center text-slate-400 text-sm mt-8">
                Marketing view skeleton - to be implemented in Phase 2
            </p>
        </div>
    );
}
