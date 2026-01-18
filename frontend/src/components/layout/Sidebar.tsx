"use client";

import { cn } from "@/lib/utils";
import {
    Code2,
    CalendarDays,
    CreditCard,
    Handshake,
    Megaphone,
    BookOpen,
    Settings,
    HelpCircle,
    LayoutDashboard,
} from "lucide-react";

export type ViewType = "overview" | "partnerships" | "marketing" | "finance" | "events" | "developers";

interface SidebarProps {
    activeView: ViewType;
    onViewChange: (view: ViewType) => void;
}

const NAV_ITEMS = [
    { id: "overview", label: "Overview", icon: LayoutDashboard },
    { id: "partnerships", label: "Partnerships", icon: Handshake },
    { id: "marketing", label: "Marketing", icon: Megaphone },
    { id: "finance", label: "Finance", icon: CreditCard },
    { id: "events", label: "Events", icon: CalendarDays },
    { id: "developers", label: "Developers", icon: Code2 },
];

const FOOTER_ITEMS = [
    { label: "Documentation", icon: BookOpen },
    { label: "Settings", icon: Settings },
    { label: "Help", icon: HelpCircle },
];

export function Sidebar({ activeView, onViewChange }: SidebarProps) {
    return (
        <div className="flex flex-col h-full bg-white">
            {/* Logo */}
            <div className="h-14 px-4 flex items-center border-b border-gray-200">
                <div className="flex items-center gap-2">
                    <div className="h-6 w-6 rounded bg-gray-900 flex items-center justify-center">
                        <span className="text-white text-xs font-bold">N</span>
                    </div>
                    <span className="font-semibold text-gray-900">Nexus</span>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 overflow-y-auto py-2">
                <div className="px-2 space-y-0.5">
                    {NAV_ITEMS.map((item) => {
                        const isActive = activeView === item.id;
                        return (
                            <button
                                key={item.id}
                                onClick={() => onViewChange(item.id as ViewType)}
                                className={cn(
                                    "w-full flex items-center gap-2.5 px-3 h-9 rounded-md text-sm transition-colors",
                                    isActive
                                        ? "bg-gray-100 text-gray-900 font-medium"
                                        : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                                )}
                            >
                                <item.icon className="h-4 w-4" />
                                <span>{item.label}</span>
                            </button>
                        );
                    })}
                </div>
            </nav>

            {/* Footer */}
            <div className="border-t border-gray-200 py-2 px-2">
                {FOOTER_ITEMS.map((item) => (
                    <button
                        key={item.label}
                        className="w-full flex items-center gap-2.5 px-3 h-8 rounded-md text-sm text-gray-500 hover:text-gray-900 hover:bg-gray-50 transition-colors"
                    >
                        <item.icon className="h-4 w-4" />
                        <span>{item.label}</span>
                    </button>
                ))}
            </div>
        </div>
    );
}
