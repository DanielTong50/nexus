import type React from "react";
import { EventsView } from "@/components/views/EventsView";

export default function EventsPage(): React.ReactElement {
    return (
        <main className="min-h-screen">
            <EventsView />
        </main>
    );
}
