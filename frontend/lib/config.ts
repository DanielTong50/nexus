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
    { name: 'Partnerships', path: '/dashboard', icon: 'Handshake' },
    { name: 'Marketing', path: '/dashboard/marketing', icon: 'Megaphone' },
    { name: 'Finance', path: '/dashboard/finance', icon: 'DollarSign' },
    { name: 'Developers', path: '/dashboard/developers', icon: 'Code' },
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
    targets: {
        judges: { current: number; target: number };
        delegates: { current: number; target: number };
        funding: { current: number; target: number };
    };
    files: { name: string; type: 'pdf' | 'xlsx' | 'docx' | 'gdoc'; url: string }[];
    timeline: { date: string; title: string; type: 'milestone' | 'task' }[];
    marketingCampaigns: {
        id: string;
        name: string;
        platform: string;
        status: 'planned' | 'active' | 'completed' | 'paused';
        startDate: string;
        endDate: string;
    }[];
    marketingFiles: { name: string; type: 'figma' | 'gdoc'; url: string }[];
    devUpdates: {
        date: string;
        title: string;
        description: string;
        type: 'feature' | 'component' | 'fix';
        author: string;
    }[];
    githubRepos: { name: string; url: string; stars: number; status: 'public' | 'private' }[];
    summary: string;
}

export const mockEvents: Event[] = [
    {
        id: 'blueprint',
        name: 'Blueprint',
        status: 'active',
        date: '2026-03-15',
        location: 'UBC Vancouver',
        attendees: 500,
        budget: 50000,
        spent: 15000,
        targets: {
            judges: { current: 6, target: 15 },
            delegates: { current: 21, target: 30 },
            funding: { current: 35000, target: 50000 }
        },
        files: [
            { name: "Outreach Compendium", type: "xlsx", url: "#" },
            { name: "Sponsorship Package v2", type: "pdf", url: "#" },
            { name: "Judge Outreach Tracker", type: "gdoc", url: "#" },
            { name: "MOU - Google", type: "pdf", url: "#" },
            { name: "MOU - Microsoft", type: "pdf", url: "#" }
        ],
        timeline: [
            { date: "2026-01-20", title: "Finalize Venue Contract", type: "milestone" },
            { date: "2026-01-25", title: "Launch Participant Applications", type: "task" },
            { date: "2026-02-01", title: "Sponsor Logos Due", type: "task" },
            { date: "2026-02-15", title: "Confirm Catering", type: "task" }
        ],
        marketingCampaigns: [
            { id: 'mc1', name: 'Early Bird Hype', platform: 'Instagram', status: 'completed', startDate: '2025-12-01', endDate: '2025-12-31' },
            { id: 'mc2', name: 'Speaker Reveal Series', platform: 'LinkedIn', status: 'active', startDate: '2026-01-10', endDate: '2026-02-10' },
            { id: 'mc3', name: 'Sponsor Shoutouts', platform: 'Twitter', status: 'planned', startDate: '2026-02-01', endDate: '2026-03-01' },
            { id: 'mc4', name: 'Delegate Applications', platform: 'All', status: 'active', startDate: '2026-01-15', endDate: '2026-02-28' }
        ],
        marketingFiles: [
            { name: "Social Media 2026 Design System", type: "figma", url: "#" },
            { name: "Launch Video Script v3", type: "gdoc", url: "#" },
            { name: "Instagram Grid Template", type: "figma", url: "#" },
            { name: "Speaker Announcement Copy", type: "gdoc", url: "#" }
        ],
        devUpdates: [
            { date: "2026-01-15", title: "Agentic Router Implementation", description: "Created the core LangGraph router for directing user queries to specific sub-agents.", type: "feature", author: "Alex" },
            { date: "2026-01-14", title: "Fixed SSE Connection Drop", description: "Resolved issue where agent stream would disconnect after 60s idle time.", type: "fix", author: "Sam" },
            { date: "2026-01-12", title: "Chat UI Component", description: "Released V1 of the chat panel with streaming support and markdown rendering.", type: "component", author: "Sarah" }
        ],
        githubRepos: [
            { name: "nexus-cortex", url: "https://github.com/nexus/cortex", stars: 124, status: 'private' },
            { name: "nexus-frontend", url: "https://github.com/nexus/frontend", stars: 45, status: 'private' },
            { name: "nexus-styles", url: "https://github.com/nexus/styles", stars: 12, status: 'public' }
        ],
        summary: "Blueprint is currently in the active planning phase. Venue contract negotiation is in final stages. Sponsorship outreach is 70% to goal with key partners Google and Microsoft signed. Judge recruitment needs attention (40% to goal). Next major milestone is application launch on Jan 25."
    },
    {
        id: 'produhacks',
        name: 'ProduHacks',
        status: 'planning',
        date: '2026-06-20',
        location: 'SFU Burnaby',
        attendees: 300,
        budget: 25000,
        spent: 5000,
        targets: {
            judges: { current: 2, target: 10 },
            delegates: { current: 5, target: 20 },
            funding: { current: 12000, target: 25000 }
        },
        files: [
            { name: "Sponsorship Deck", type: "pdf", url: "#" },
            { name: "Budget Planner", type: "xlsx", url: "#" }
        ],
        timeline: [
            { date: "2026-03-01", title: "Venue Scouting", type: "task" },
            { date: "2026-04-15", title: "Website Launch", type: "milestone" }
        ],
        marketingCampaigns: [
            { id: 'mc5', name: 'Teaser Campaign', platform: 'Instagram', status: 'planned', startDate: '2026-03-01', endDate: '2026-04-01' },
            { id: 'mc6', name: 'Brand Awareness', platform: 'LinkedIn', status: 'planned', startDate: '2026-04-01', endDate: '2026-05-01' }
        ],
        marketingFiles: [
            { name: "Brand Identity v1", type: "figma", url: "#" },
            { name: "Website Copy Draft", type: "gdoc", url: "#" }
        ],
        devUpdates: [],
        githubRepos: [],
        summary: "ProduHacks is in early planning. Budget approved. Core team assembled. Sponsorship deck finalized and outreach begun. Venue scouting is the primary focus for March."
    },
    {
        id: 'techstrat',
        name: 'TechStrat',
        status: 'planning',
        date: '2026-09-10',
        location: 'Downtown Vancouver',
        attendees: 150,
        budget: 15000,
        spent: 2000,
        targets: {
            judges: { current: 0, target: 8 },
            delegates: { current: 0, target: 15 },
            funding: { current: 2000, target: 15000 }
        },
        files: [],
        timeline: [
            { date: "2026-05-01", title: "Kickoff Meeting", type: "milestone" }
        ],
        marketingCampaigns: [],
        marketingFiles: [],
        devUpdates: [],
        githubRepos: [],
        summary: "TechStrat is in the ideation phase. Initial budget allocated. Theme selection pending."
    }
];

// Partnership-specific types and data
export interface Partner {
    id: string;
    name: string;
    category: 'sponsor' | 'judge' | 'mentor' | 'partner';
    tier: 'platinum' | 'gold' | 'silver' | 'bronze' | 'in-kind' | 'none';
    status: 'in_talks' | 'rejected' | 'agreed' | 'signed';
    mouStatus?: 'sent' | 'signed' | 'paid' | 'followed-up' | 'none';
    amount: number;
    eventId: string;
    contactName: string;
    contactEmail: string;
    lastContact: string;
}

export const mockPartners: Partner[] = [
    // Blueprint partners
    {
        id: 'p1',
        name: 'Google',
        category: 'sponsor',
        tier: 'platinum',
        status: 'signed',
        mouStatus: 'paid',
        amount: 15000,
        eventId: 'blueprint',
        contactName: 'Sarah Chen',
        contactEmail: 'sarah@google.com',
        lastContact: '2026-01-15'
    },
    {
        id: 'p2',
        name: 'Microsoft',
        category: 'sponsor',
        tier: 'gold',
        status: 'in_talks',
        mouStatus: 'sent',
        amount: 10000,
        eventId: 'blueprint',
        contactName: 'James Wilson',
        contactEmail: 'james@microsoft.com',
        lastContact: '2026-01-10'
    },
    {
        id: 'p3',
        name: 'Dr. Emily Zhang',
        category: 'judge',
        tier: 'none',
        status: 'agreed',
        mouStatus: 'none',
        amount: 0,
        eventId: 'blueprint',
        contactName: 'Dr. Emily Zhang',
        contactEmail: 'emily.z@stanford.edu',
        lastContact: '2026-01-14'
    },
    {
        id: 'p4',
        name: 'Andreessen Horowitz',
        category: 'judge',
        tier: 'none',
        status: 'rejected',
        mouStatus: 'none',
        amount: 0,
        eventId: 'blueprint',
        contactName: 'David Kim',
        contactEmail: 'david@a16z.com',
        lastContact: '2026-01-11'
    },
    // ProduHacks partners
    {
        id: 'p5',
        name: 'AWS',
        category: 'sponsor',
        tier: 'gold',
        status: 'agreed',
        mouStatus: 'signed',
        amount: 8000,
        eventId: 'produhacks',
        contactName: 'Mark Thompson',
        contactEmail: 'mark@aws.com',
        lastContact: '2026-01-08'
    },
    {
        id: 'p6',
        name: 'Figma',
        category: 'sponsor',
        tier: 'silver',
        status: 'in_talks',
        mouStatus: 'followed-up',
        amount: 5000,
        eventId: 'produhacks',
        contactName: 'Lisa Park',
        contactEmail: 'lisa@figma.com',
        lastContact: '2026-01-12'
    },
    // TechStrat partners
    {
        id: 'p7',
        name: 'Deloitte',
        category: 'sponsor',
        tier: 'gold',
        status: 'signed',
        mouStatus: 'sent',
        amount: 7500,
        eventId: 'techstrat',
        contactName: 'Michael Lee',
        contactEmail: 'mlee@deloitte.com',
        lastContact: '2026-01-05'
    },
    {
        id: 'p8',
        name: 'McKinsey',
        category: 'partner',
        tier: 'silver',
        status: 'in_talks',
        mouStatus: 'none',
        amount: 5000,
        eventId: 'techstrat',
        contactName: 'Anna Roberts',
        contactEmail: 'aroberts@mckinsey.com',
        lastContact: '2026-01-09'
    },
];

