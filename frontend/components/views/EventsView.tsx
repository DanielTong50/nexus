"use client";

interface EventsViewProps {
    // Add props as needed in Phase 2
}

/**
 * Events view - displays event listings.
 * Skeleton to be fully implemented in Phase 2.
 */
export function EventsView({ }: EventsViewProps): React.ReactElement {
    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-primary">Events</h1>
            </div>

            {/* Content Placeholder */}
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {/* Placeholder Event Cards */}
                {[1, 2, 3].map((i) => (
                    <div
                        key={i}
                        className="p-6 bg-white rounded-lg shadow-sm border border-slate-200"
                    >
                        <div className="h-4 w-3/4 bg-slate-200 rounded animate-pulse mb-4"></div>
                        <div className="h-3 w-1/2 bg-slate-100 rounded animate-pulse mb-2"></div>
                        <div className="h-3 w-2/3 bg-slate-100 rounded animate-pulse"></div>
                    </div>
                ))}
            </div>

            {/* Skeleton message */}
            <p className="text-center text-slate-400 text-sm mt-8">
                Events view skeleton - to be implemented with event cards in Phase 2
            </p>
        </div>
    );
}
