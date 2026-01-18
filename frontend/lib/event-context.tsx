"use client";

import React, { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import { useSearchParams, useRouter } from "next/navigation";

// Available events
export const EVENTS = [
    { id: "blueprint", name: "Blueprint", description: "Annual flagship hackathon" },
    { id: "produhacks", name: "ProduHacks", description: "Product-focused hackathon" },
    { id: "techstrat", name: "TechStrat", description: "Tech strategy competition" },
] as const;

export type EventId = typeof EVENTS[number]["id"];

interface EventContextType {
    eventId: EventId | null;
    eventName: string | null;
    setEvent: (id: EventId) => void;
    clearEvent: () => void;
}

const EventContext = createContext<EventContextType | undefined>(undefined);

export function EventProvider({ children }: { children: ReactNode }) {
    const [eventId, setEventId] = useState<EventId | null>(null);
    const searchParams = useSearchParams();
    const router = useRouter();

    // Sync with URL param on mount
    useEffect(() => {
        const urlEvent = searchParams.get("event") as EventId | null;
        if (urlEvent && EVENTS.some(e => e.id === urlEvent)) {
            setEventId(urlEvent);
        }
    }, [searchParams]);

    const setEvent = (id: EventId) => {
        setEventId(id);
        // Update URL
        router.push(`/dashboard?event=${id}`);
    };

    const clearEvent = () => {
        setEventId(null);
        router.push("/");
    };

    const eventName = eventId
        ? EVENTS.find(e => e.id === eventId)?.name ?? null
        : null;

    return (
        <EventContext.Provider value={{ eventId, eventName, setEvent, clearEvent }}>
            {children}
        </EventContext.Provider>
    );
}

export function useEvent() {
    const context = useContext(EventContext);
    if (context === undefined) {
        throw new Error("useEvent must be used within an EventProvider");
    }
    return context;
}
