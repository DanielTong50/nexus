/**
 * Central configuration for the Nexus frontend.
 * Never hardcode values - always use this config.
 */

export const colors = {
    primary: '#334155',     // slate-700
    secondary: '#e2e8f0',   // slate-200
    background: '#f8fafc',  // slate-50
    accent: '#3b82f6',      // blue-500
    success: '#22c55e',     // green-500
    warning: '#f59e0b',     // amber-500
    error: '#ef4444',       // red-500
} as const;

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface NavItem {
    name: string;
    path: string;
    icon: 'Calendar' | 'Handshake' | 'Megaphone' | 'DollarSign' | 'Code';
}

export const navItems: NavItem[] = [
    { name: 'Events', path: '/', icon: 'Calendar' },
    { name: 'Partnerships', path: '/partnerships', icon: 'Handshake' },
    { name: 'Marketing', path: '/marketing', icon: 'Megaphone' },
    { name: 'Finance', path: '/finance', icon: 'DollarSign' },
    { name: 'Developers', path: '/developers', icon: 'Code' },
];
