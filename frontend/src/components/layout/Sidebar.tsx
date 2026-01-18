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
    ExternalLink
} from "lucide-react";

export type ViewType = "partnerships" | "marketing" | "finance" | "events" | "developers";

interface SidebarProps {
    activeView: ViewType;
    onViewChange: (view: ViewType) => void;
}

const NAV_SECTIONS = [
    {
        title: "Workspaces",
        items: [
            { id: "partnerships", label: "Partnerships", icon: Handshake },
            { id: "marketing", label: "Marketing", icon: Megaphone },
            { id: "finance", label: "Finance", icon: CreditCard },
            { id: "events", label: "Events", icon: CalendarDays },
            { id: "developers", label: "Developers", icon: Code2 },
        ]
    }
];

const FOOTER_ITEMS = [
    { label: "Documentation", icon: BookOpen, href: "#" },
    { label: "Settings", icon: Settings, href: "#" },
    { label: "Help", icon: HelpCircle, href: "#" },
];

export function Sidebar({ activeView, onViewChange }: SidebarProps) {
    return (
        <div className="flex flex-col h-full">
            {/* Logo */}
            <div className="h-14 px-5 flex items-center border-b border-slate-200">
                <div className="flex items-center gap-2">
                    <div className="h-6 w-6 rounded bg-slate-900 flex items-center justify-center">
                        <span className="text-white text-xs font-bold">N</span>
                    </div>
                    <span className="font-semibold text-slate-900 tracking-tight">Nexus</span>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 overflow-y-auto py-4">
                {NAV_SECTIONS.map((section) => (
                    <div key={section.title} className="mb-6">
                        <div className="px-5 mb-2">
                            <span className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">
                                {section.title}
                            </span>
                        </div>
                        <div className="space-y-0.5 px-3">
                            {section.items.map((item) => {
                                const isActive = activeView === item.id;
                                return (
                                    <button
                                        key={item.id}
                                        onClick={() => onViewChange(item.id as ViewType)}
                                        className={cn(
                                            "w-full flex items-center gap-3 px-3 h-9 rounded-md text-sm transition-colors",
                                            isActive
                                                ? "bg-slate-100 text-slate-900 font-medium"
                                                : "text-slate-500 hover:text-slate-900 hover:bg-slate-50"
                                        )}
                                    >
                                        <item.icon className="h-4 w-4" />
                                        <span>{item.label}</span>
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                ))}
            </nav>

            {/* Footer Links */}
            <div className="border-t border-slate-200 py-3 px-3">
                {FOOTER_ITEMS.map((item) => (
                    <a
                        key={item.label}
                        href={item.href}
                        className="flex items-center gap-3 px-3 h-8 rounded-md text-sm text-slate-500 hover:text-slate-900 hover:bg-slate-50 transition-colors"
                    >
                        <item.icon className="h-4 w-4" />
                        <span>{item.label}</span>
                        {item.href !== "#" && <ExternalLink className="h-3 w-3 ml-auto" />}
                    </a>
                ))}
            </div>
        </div>
    );
}
