"use client";

import { useEvent } from "@/lib/event-context";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { PartnershipsView } from "@/components/views/PartnershipsView";

export default function DashboardPage() {
    const { eventId, eventName } = useEvent();
    const router = useRouter();

    // Redirect to home if no event selected
    useEffect(() => {
        if (!eventId) {
            router.push("/");
        }
    }, [eventId, router]);

    if (!eventId) {
        return (
            <div className="flex items-center justify-center h-full">
                <p className="text-muted-foreground">Loading...</p>
            </div>
        );
    }

    return (
        <div className="h-full">
            {/* Event Header */}
            <div className="border-b border-border px-6 py-4">
                <h1 className="text-lg font-semibold">{eventName}</h1>
                <p className="text-sm text-muted-foreground">Dashboard</p>
            </div>

            {/* Content - Partnerships by default */}
            <PartnershipsView />
        </div>
    );
}
