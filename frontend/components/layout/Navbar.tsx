"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import { navItems, type NavItem } from "@/lib/config";
import { useEvent, EVENTS } from "@/lib/event-context";
import { cn } from "@/lib/utils";
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ChevronDown } from "lucide-react";

interface NavbarProps {
    collapsed?: boolean;
    onChatToggle?: () => void;
}

/**
 * Icon component - slightly larger, bolder icons
 */
function NavIcon({ icon, className }: { icon: NavItem['icon']; className?: string }): React.ReactElement {
    const iconClass = cn("w-5 h-5", className);

    switch (icon) {
        case 'Calendar':
            return (
                <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
            );
        case 'Handshake':
            return (
                <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
                </svg>
            );
        case 'Megaphone':
            return (
                <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M10.34 15.84c-.688-.06-1.386-.09-2.09-.09H7.5a4.5 4.5 0 110-9h.75c.704 0 1.402-.03 2.09-.09m0 9.18c.253.962.584 1.892.985 2.783.247.55.06 1.21-.463 1.511l-.657.38c-.551.318-1.26.117-1.527-.461a20.845 20.845 0 01-1.44-4.282m3.102.069a18.03 18.03 0 01-.59-4.59c0-1.586.205-3.124.59-4.59m0 9.18a23.848 23.848 0 018.835 2.535M10.34 6.66a23.847 23.847 0 008.835-2.535m0 0A23.74 23.74 0 0018.795 3m.38 1.125a23.91 23.91 0 011.014 5.395m-1.014 8.855c-.118.38-.245.754-.38 1.125m.38-1.125a23.91 23.91 0 001.014-5.395m0-3.46c.495.413.811 1.035.811 1.73 0 .695-.316 1.317-.811 1.73m0-3.46a24.347 24.347 0 010 3.46" />
                </svg>
            );
        case 'DollarSign':
            return (
                <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            );
        case 'Code':
            return (
                <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5" />
                </svg>
            );
    }
}

/**
 * Sidebar navigation with event switcher
 */
export function Navbar({ collapsed = false, onChatToggle }: NavbarProps): React.ReactElement {
    const pathname = usePathname();
    const { eventId, eventName, setEvent, clearEvent } = useEvent();

    // Don't show navbar on landing page
    if (!eventId) {
        return <></>;
    }

    return (
        <aside
            className={cn(
                "h-screen bg-background flex flex-col border-r border-border transition-all duration-300",
                collapsed ? "w-16" : "w-60"
            )}
        >
            {/* Logo + Event Switcher */}
            <div className="border-b border-border">
                {/* Logo */}
                <div className={cn(
                    "h-14 flex items-center border-b border-border",
                    collapsed ? "justify-center px-3" : "px-5"
                )}>
                    <Link href="/" onClick={clearEvent}>
                        <div className={cn("relative", collapsed ? "w-8 h-8" : "w-28 h-9")}>
                            <Image src="/logo.png" alt="Nexus" fill className="object-contain" />
                        </div>
                    </Link>
                </div>

                {/* Event Switcher */}
                {!collapsed && (
                    <div className="px-3 py-3">
                        <DropdownMenu>
                            <DropdownMenuTrigger className="w-full flex items-center justify-between px-3 py-2 rounded-md bg-secondary hover:bg-secondary/80 text-sm font-medium transition-colors">
                                <span>{eventName}</span>
                                <ChevronDown className="h-4 w-4 text-muted-foreground" />
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="start" className="w-52">
                                {EVENTS.map((event) => (
                                    <DropdownMenuItem
                                        key={event.id}
                                        onClick={() => setEvent(event.id)}
                                        className={cn(
                                            "cursor-pointer",
                                            eventId === event.id && "bg-secondary"
                                        )}
                                    >
                                        {event.name}
                                    </DropdownMenuItem>
                                ))}
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </div>
                )}
            </div>

            {/* Nav Items */}
            <nav className="flex-1 py-4 px-3 space-y-4">
                {/* Chat Button */}
                <button
                    onClick={onChatToggle}
                    className={cn(
                        "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all shadow-sm group",
                        collapsed ? "justify-center px-2 bg-transparent" : "bg-gradient-to-r from-primary/10 to-blue-500/10 hover:from-primary/20 hover:to-blue-500/20 border border-primary/20",
                    )}
                    title="Open AI Chat"
                >
                    <div className={cn(
                        "flex items-center justify-center rounded-md text-primary transition-transform group-hover:scale-110",
                        collapsed ? "w-8 h-8" : "w-5 h-5"
                    )}>
                        <svg className={cn("w-5 h-5", collapsed && "w-6 h-6")} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
                        </svg>
                    </div>
                    {!collapsed && <span className="font-semibold text-primary">AI Chat</span>}
                </button>

                <ul className="space-y-1">
                    {navItems.map((item) => {
                        const isActive = pathname === item.path || pathname.startsWith(item.path + "/");
                        return (
                            <li key={item.path}>
                                <Link
                                    href={`${item.path}?event=${eventId}`}
                                    className={cn(
                                        "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors",
                                        collapsed && "justify-center px-2",
                                        isActive
                                            ? "bg-secondary text-foreground font-semibold"
                                            : "text-muted-foreground hover:text-foreground hover:bg-secondary/50 font-medium"
                                    )}
                                    title={collapsed ? item.name : undefined}
                                >
                                    <NavIcon icon={item.icon} />
                                    {!collapsed && <span>{item.name}</span>}
                                </Link>
                            </li>
                        );
                    })}
                </ul>
            </nav>

            {/* Footer */}
            <div className={cn(
                "py-4 px-5 border-t border-border text-xs text-muted-foreground",
                collapsed && "text-center px-2"
            )}>
                {collapsed ? "v1" : "Nexus v0.1.0"}
            </div>
        </aside>
    );
}
