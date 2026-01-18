/**
 * Mock data for Nexus frontend development
 * This will be replaced with real API calls in production
 */

// Event Types
export type EventStatus = "upcoming" | "in-progress" | "completed" | "planning";

export interface NexusEvent {
  id: string;
  name: string;
  description: string;
  date: string;
  endDate?: string;
  location: string;
  status: EventStatus;
  attendees?: number;
  budget?: number;
  budgetUsed?: number;
  teams: string[];
  image?: string;
}

// Partner Types
export type PartnerStatus = "confirmed" | "verbal" | "pending" | "rejected" | "contacted";
export type PartnerCategory = "sponsor" | "judge" | "mentor" | "student-mentor";
export type SponsorTier = "platinum" | "gold" | "silver" | "bronze" | "in-kind";

export interface Partner {
  id: string;
  name: string;
  category: PartnerCategory;
  status: PartnerStatus;
  tier?: SponsorTier;
  amount?: number;
  contactName?: string;
  contactEmail?: string;
  eventId: string;
  notes?: string;
  lastContact?: string;
}

// Marketing Types
export type PostStatus = "scheduled" | "draft" | "published" | "needs-review";
export type Platform = "instagram" | "linkedin" | "twitter";

export interface SocialPost {
  id: string;
  platform: Platform;
  content: string;
  scheduledDate?: string;
  publishedDate?: string;
  status: PostStatus;
  eventId: string;
  imageUrl?: string;
  campaign?: string;
}

// Finance Types
export type DocumentStatus = "draft" | "pending" | "approved" | "sent" | "paid";

export interface FinanceDocument {
  id: string;
  type: "mou" | "invoice";
  partnerName: string;
  amount: number;
  status: DocumentStatus;
  eventId: string;
  createdAt: string;
  dueDate?: string;
}

export interface BudgetCategory {
  name: string;
  allocated: number;
  spent: number;
  eventId: string;
}

// Developer Types
export type IssueStatus = "open" | "in-progress" | "review" | "closed";
export type IssuePriority = "low" | "medium" | "high" | "critical";

export interface GitHubIssue {
  id: string;
  title: string;
  description: string;
  status: IssueStatus;
  priority: IssuePriority;
  assignee?: string;
  labels: string[];
  repo: string;
  createdAt: string;
}

// ============== MOCK DATA ==============

export const MOCK_EVENTS: NexusEvent[] = [
  {
    id: "blueprint-2025",
    name: "Blueprint 2025",
    description: "Annual flagship hackathon bringing together 500+ students to build innovative solutions",
    date: "2025-03-15",
    endDate: "2025-03-16",
    location: "Engineering Building",
    status: "planning",
    attendees: 500,
    budget: 25000,
    budgetUsed: 8500,
    teams: ["partnerships", "marketing", "finance", "events", "developers"],
  },
  {
    id: "hackathon-spring",
    name: "Spring Hackathon",
    description: "24-hour hackathon focused on sustainability and green tech solutions",
    date: "2025-04-20",
    endDate: "2025-04-21",
    location: "Student Center",
    status: "upcoming",
    attendees: 200,
    budget: 10000,
    budgetUsed: 2000,
    teams: ["partnerships", "marketing", "events"],
  },
  {
    id: "workshop-series",
    name: "Workshop Series",
    description: "Weekly technical workshops covering web dev, ML, and mobile development",
    date: "2025-02-01",
    endDate: "2025-04-30",
    location: "Various",
    status: "in-progress",
    attendees: 50,
    budget: 3000,
    budgetUsed: 1500,
    teams: ["marketing", "events", "developers"],
  },
  {
    id: "tech-talks",
    name: "Tech Talks Fall",
    description: "Industry speaker series featuring engineers from top tech companies",
    date: "2024-10-15",
    endDate: "2024-12-10",
    location: "Lecture Hall A",
    status: "completed",
    attendees: 150,
    budget: 5000,
    budgetUsed: 4800,
    teams: ["partnerships", "marketing", "events"],
  },
];

export const MOCK_PARTNERS: Partner[] = [
  {
    id: "google-bp25",
    name: "Google",
    category: "sponsor",
    status: "confirmed",
    tier: "platinum",
    amount: 5000,
    contactName: "Sarah Chen",
    contactEmail: "sarah@google.com",
    eventId: "blueprint-2025",
    lastContact: "2025-01-15",
  },
  {
    id: "microsoft-bp25",
    name: "Microsoft",
    category: "sponsor",
    status: "verbal",
    tier: "gold",
    amount: 3000,
    contactName: "John Smith",
    contactEmail: "john@microsoft.com",
    eventId: "blueprint-2025",
    lastContact: "2025-01-10",
  },
  {
    id: "meta-bp25",
    name: "Meta",
    category: "sponsor",
    status: "pending",
    tier: "gold",
    amount: 3000,
    contactName: "Lisa Wang",
    contactEmail: "lisa@meta.com",
    eventId: "blueprint-2025",
    lastContact: "2025-01-05",
  },
  {
    id: "aws-bp25",
    name: "AWS",
    category: "sponsor",
    status: "contacted",
    tier: "silver",
    amount: 1500,
    eventId: "blueprint-2025",
  },
  {
    id: "judge-1",
    name: "Dr. Emily Zhang",
    category: "judge",
    status: "confirmed",
    contactEmail: "ezhang@university.edu",
    eventId: "blueprint-2025",
  },
  {
    id: "judge-2",
    name: "Marcus Johnson",
    category: "judge",
    status: "pending",
    contactEmail: "marcus@startup.com",
    eventId: "blueprint-2025",
    notes: "CTO at local startup",
  },
  {
    id: "mentor-1",
    name: "Alex Rivera",
    category: "mentor",
    status: "confirmed",
    eventId: "blueprint-2025",
  },
];

export const MOCK_POSTS: SocialPost[] = [
  {
    id: "post-1",
    platform: "instagram",
    content: "🚀 Blueprint 2025 is coming! Get ready for the biggest hackathon of the year. Registration opens soon! #Blueprint2025 #Hackathon",
    scheduledDate: "2025-02-01",
    status: "scheduled",
    eventId: "blueprint-2025",
    campaign: "Launch Campaign",
  },
  {
    id: "post-2",
    platform: "linkedin",
    content: "We're excited to announce that Google is our Platinum Sponsor for Blueprint 2025! Thank you for supporting student innovation.",
    status: "draft",
    eventId: "blueprint-2025",
    campaign: "Sponsor Announcements",
  },
  {
    id: "post-3",
    platform: "instagram",
    content: "Workshop tomorrow! Learn React from industry experts. Don't miss it! 📚",
    publishedDate: "2025-01-20",
    status: "published",
    eventId: "workshop-series",
    campaign: "Workshop Promos",
  },
];

export const MOCK_FINANCE_DOCS: FinanceDocument[] = [
  {
    id: "mou-google",
    type: "mou",
    partnerName: "Google",
    amount: 5000,
    status: "approved",
    eventId: "blueprint-2025",
    createdAt: "2025-01-10",
  },
  {
    id: "invoice-google",
    type: "invoice",
    partnerName: "Google",
    amount: 5000,
    status: "sent",
    eventId: "blueprint-2025",
    createdAt: "2025-01-12",
    dueDate: "2025-02-12",
  },
  {
    id: "mou-microsoft",
    type: "mou",
    partnerName: "Microsoft",
    amount: 3000,
    status: "pending",
    eventId: "blueprint-2025",
    createdAt: "2025-01-14",
  },
];

export const MOCK_BUDGET: BudgetCategory[] = [
  { name: "Venue", allocated: 5000, spent: 2500, eventId: "blueprint-2025" },
  { name: "Food & Beverages", allocated: 8000, spent: 3000, eventId: "blueprint-2025" },
  { name: "Prizes", allocated: 5000, spent: 0, eventId: "blueprint-2025" },
  { name: "Marketing", allocated: 3000, spent: 1500, eventId: "blueprint-2025" },
  { name: "Swag", allocated: 2000, spent: 1000, eventId: "blueprint-2025" },
  { name: "Miscellaneous", allocated: 2000, spent: 500, eventId: "blueprint-2025" },
];

export const MOCK_ISSUES: GitHubIssue[] = [
  {
    id: "issue-1",
    title: "Implement registration form",
    description: "Create the hacker registration form with validation",
    status: "in-progress",
    priority: "high",
    assignee: "Alex",
    labels: ["frontend", "feature"],
    repo: "blueprint-website",
    createdAt: "2025-01-10",
  },
  {
    id: "issue-2",
    title: "Add sponsor logo carousel",
    description: "Display sponsor logos on the landing page",
    status: "open",
    priority: "medium",
    labels: ["frontend", "enhancement"],
    repo: "blueprint-website",
    createdAt: "2025-01-12",
  },
  {
    id: "issue-3",
    title: "Set up CI/CD pipeline",
    description: "Configure GitHub Actions for automated deployment",
    status: "review",
    priority: "high",
    assignee: "Jordan",
    labels: ["devops", "infrastructure"],
    repo: "blueprint-website",
    createdAt: "2025-01-08",
  },
  {
    id: "issue-4",
    title: "Fix mobile navigation",
    description: "Navigation menu not working on mobile devices",
    status: "open",
    priority: "critical",
    labels: ["bug", "frontend"],
    repo: "blueprint-website",
    createdAt: "2025-01-15",
  },
];

// Helper functions
export function getEventById(id: string): NexusEvent | undefined {
  return MOCK_EVENTS.find((e) => e.id === id);
}

export function getPartnersByEvent(eventId: string): Partner[] {
  return MOCK_PARTNERS.filter((p) => p.eventId === eventId);
}

export function getPostsByEvent(eventId: string): SocialPost[] {
  return MOCK_POSTS.filter((p) => p.eventId === eventId);
}

export function getFinanceDocsByEvent(eventId: string): FinanceDocument[] {
  return MOCK_FINANCE_DOCS.filter((d) => d.eventId === eventId);
}

export function getBudgetByEvent(eventId: string): BudgetCategory[] {
  return MOCK_BUDGET.filter((b) => b.eventId === eventId);
}

export function getIssuesByRepo(repo: string): GitHubIssue[] {
  return MOCK_ISSUES.filter((i) => i.repo === repo);
}

// Stats helpers
export function getTotalRaised(eventId: string): number {
  return MOCK_PARTNERS
    .filter((p) => p.eventId === eventId && p.status === "confirmed" && p.amount)
    .reduce((sum, p) => sum + (p.amount || 0), 0);
}

export function getPendingAmount(eventId: string): number {
  return MOCK_PARTNERS
    .filter((p) => p.eventId === eventId && (p.status === "verbal" || p.status === "pending") && p.amount)
    .reduce((sum, p) => sum + (p.amount || 0), 0);
}
