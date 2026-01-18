/**
 * Central configuration for the Nexus frontend.
 * Never hardcode values - always use this config.
 */

export const colors = {
    // Clean minimal theme - light blue accent
    primary: '#3b82f6',     // Light blue (professional)
    secondary: '#f4f4f5',   // Very light grey
    background: '#ffffff',  // White
    accent: '#3b82f6',      // Light blue
    success: '#22c55e',     // Green
    warning: '#eab308',     // Yellow
    error: '#ef4444',       // Red
    card: '#ffffff',        // White
    border: '#e5e7eb',      // Light grey border
    muted: '#6b7280',       // Grey text
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

export interface Event {
    id: string;
    name: string;
    status: 'active' | 'planning' | 'concluded';
    date: string;
    location: string;
    attendees: number;
    budget: number;
    spent: number;
}

export const mockEvents: Event[] = [
    {
        id: '1',
        name: 'TechSummit 2026',
        status: 'active',
        date: '2026-03-15',
        location: 'San Francisco, CA',
        attendees: 1500,
        budget: 500000,
        spent: 125000
    },
    {
        id: '2',
        name: 'DevConnect London',
        status: 'planning',
        date: '2026-06-20',
        location: 'London, UK',
        attendees: 800,
        budget: 250000,
        spent: 15000
    },
    {
        id: '3',
        name: 'AI Innovators Gala',
        status: 'active',
        date: '2026-02-10',
        location: 'New York, NY',
        attendees: 300,
        budget: 150000,
        spent: 95000
    },
    {
        id: '4',
        name: 'Global Hackathon',
        status: 'planning',
        date: '2026-08-01',
        location: 'Online',
        attendees: 5000,
        budget: 50000,
        spent: 5000
    }
];

// Partnership-specific types and data
export interface Partner {
    id: string;
    name: string;
    category: 'sponsor' | 'judge' | 'mentor' | 'partner';
    tier: 'platinum' | 'gold' | 'silver' | 'bronze' | 'in-kind' | 'none';
    status: 'confirmed' | 'pending' | 'negotiating' | 'declined';
    amount: number;
    eventId: string;
    contactName: string;
    contactEmail: string;
    lastContact: string;
}

export const mockPartners: Partner[] = [
    {
        id: 'p1',
        name: 'Google',
        category: 'sponsor',
        tier: 'platinum',
        status: 'confirmed',
        amount: 50000,
        eventId: '1',
        contactName: 'Sarah Chen',
        contactEmail: 'sarah@google.com',
        lastContact: '2026-01-15'
    },
    {
        id: 'p2',
        name: 'Microsoft',
        category: 'sponsor',
        tier: 'gold',
        status: 'pending',
        amount: 25000,
        eventId: '1',
        contactName: 'James Wilson',
        contactEmail: 'james@microsoft.com',
        lastContact: '2026-01-10'
    },
    {
        id: 'p3',
        name: 'Meta',
        category: 'sponsor',
        tier: 'gold',
        status: 'negotiating',
        amount: 20000,
        eventId: '1',
        contactName: 'Lisa Park',
        contactEmail: 'lisa@meta.com',
        lastContact: '2026-01-12'
    },
    {
        id: 'p4',
        name: 'AWS',
        category: 'sponsor',
        tier: 'silver',
        status: 'confirmed',
        amount: 10000,
        eventId: '2',
        contactName: 'Mark Thompson',
        contactEmail: 'mark@aws.com',
        lastContact: '2026-01-08'
    },
    {
        id: 'p5',
        name: 'Dr. Emily Zhang',
        category: 'judge',
        tier: 'none',
        status: 'confirmed',
        amount: 0,
        eventId: '1',
        contactName: 'Dr. Emily Zhang',
        contactEmail: 'emily.z@stanford.edu',
        lastContact: '2026-01-14'
    },
    {
        id: 'p6',
        name: 'Andreessen Horowitz',
        category: 'judge',
        tier: 'none',
        status: 'pending',
        amount: 0,
        eventId: '1',
        contactName: 'David Kim',
        contactEmail: 'david@a16z.com',
        lastContact: '2026-01-11'
    },
];
