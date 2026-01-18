"use client";

import Shell from "@/components/layout/Shell";
import { PageTransition } from "@/components/ui/PageTransition";

export default function DashboardPage() {
    return (
        <PageTransition loaderDuration={800}>
            <Shell />
        </PageTransition>
    );
}
