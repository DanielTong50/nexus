"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { navItems, type NavItem } from "@/lib/config";
import { cn } from "@/lib/utils";

interface NavbarProps {
    collapsed?: boolean;
}

/**
 * Icon component that renders the appropriate icon based on name
 */
function NavIcon({ icon, className }: { icon: NavItem['icon']; className?: string }): React.ReactElement {
    const iconClass = cn("w-5 h-5", className);

    switch (icon) {
        case 'Calendar':
            return (
                <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
            );
        case 'Handshake':
            return (
                <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
            );
        case 'Megaphone':
            return (
                <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
                </svg>
            );
        case 'DollarSign':
            return (
                <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            );
        case 'Code':
            return (
                <svg className={iconClass} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
            );
    }
}

/**
 * Left sidebar navigation with all 5 nav items.
 * Includes collapse logic for when chat panel opens.
 */
export function Navbar({ collapsed = false }: NavbarProps): React.ReactElement {
    const pathname = usePathname();

    return (
        <nav
            className={cn(
                "h-screen bg-primary text-secondary flex flex-col transition-all duration-300",
                collapsed ? "w-16" : "w-64"
            )}
            role="navigation"
            aria-label="Main navigation"
        >
            {/* Logo/Brand */}
            <div className={cn(
                "flex items-center h-16 px-4 border-b border-slate-600",
                collapsed ? "justify-center" : "justify-start"
            )}>
                <span className="text-xl font-bold text-white">
                    {collapsed ? "N" : "Nexus"}
                </span>
            </div>

            {/* Navigation Items */}
            <ul className="flex-1 py-4 space-y-1">
                {navItems.map((item) => {
                    const isActive = pathname === item.path;

                    return (
                        <li key={item.path}>
                            <Link
                                href={item.path}
                                className={cn(
                                    "flex items-center px-4 py-3 mx-2 rounded-lg transition-colors duration-200",
                                    "hover:bg-slate-600 focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:ring-offset-primary",
                                    isActive && "bg-slate-600 text-white",
                                    collapsed ? "justify-center" : "gap-3"
                                )}
                                aria-current={isActive ? "page" : undefined}
                                title={collapsed ? item.name : undefined}
                            >
                                <NavIcon icon={item.icon} />
                                {!collapsed && <span>{item.name}</span>}
                            </Link>
                        </li>
                    );
                })}
            </ul>

            {/* Footer */}
            <div className={cn(
                "p-4 border-t border-slate-600 text-sm text-slate-400",
                collapsed ? "text-center" : ""
            )}>
                {collapsed ? "v1" : "Nexus v0.1.0"}
            </div>
        </nav>
    );
}
