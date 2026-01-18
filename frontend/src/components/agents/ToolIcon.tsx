"use client";

import { Wrench } from "lucide-react";

// Inline SVG icons for tools (more reliable than CDN)
const SlackIcon = ({ size = 16, className = "" }: { size?: number; className?: string }) => (
    <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="#E01E5A">
        <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zM6.313 15.165a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zM8.834 6.313a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zM18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zM17.688 8.834a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.165 0a2.528 2.528 0 0 1 2.523 2.522v6.312zM15.165 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.165 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52zM15.165 17.688a2.527 2.527 0 0 1-2.52-2.523 2.526 2.526 0 0 1 2.52-2.52h6.313A2.527 2.527 0 0 1 24 15.165a2.528 2.528 0 0 1-2.522 2.523h-6.313z"/>
    </svg>
);

const GoogleSheetsIcon = ({ size = 16, className = "" }: { size?: number; className?: string }) => (
    <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="#34A853">
        <path d="M19.385 2H4.615A2.615 2.615 0 0 0 2 4.615v14.77A2.615 2.615 0 0 0 4.615 22h14.77A2.615 2.615 0 0 0 22 19.385V4.615A2.615 2.615 0 0 0 19.385 2zM8 17H6v-2h2v2zm0-4H6v-2h2v2zm0-4H6V7h2v2zm4 8h-2v-2h2v2zm0-4h-2v-2h2v2zm0-4h-2V7h2v2zm6 8h-4v-2h4v2zm0-4h-4v-2h4v2zm0-4h-4V7h4v2z"/>
    </svg>
);

const GoogleDocsIcon = ({ size = 16, className = "" }: { size?: number; className?: string }) => (
    <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="#4285F4">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zm-1 2l5 5h-5V4zM6 20V4h6v6h6v10H6zm2-6h8v2H8v-2zm0-4h8v2H8v-2zm0 8h5v2H8v-2z"/>
    </svg>
);

const NotionIcon = ({ size = 16, className = "" }: { size?: number; className?: string }) => (
    <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="#000000">
        <path d="M4.459 4.208c.746.606 1.026.56 2.428.466l13.215-.793c.28 0 .047-.28-.046-.326L17.86 1.968c-.42-.326-.98-.7-2.055-.607L3.01 2.295c-.466.046-.56.28-.374.466l1.823 1.447zm.793 3.08v13.904c0 .747.373 1.027 1.214.98l14.523-.84c.841-.046.934-.56.934-1.167V6.354c0-.606-.233-.933-.747-.886l-15.177.887c-.56.047-.747.327-.747.933zm14.337.745c.093.42 0 .84-.42.888l-.7.14v10.264c-.608.327-1.168.514-1.635.514-.747 0-.934-.234-1.495-.933l-4.577-7.186v6.952l1.448.327s0 .84-1.168.84l-3.22.186c-.093-.186 0-.653.327-.746l.84-.233V9.854L7.822 9.76c-.094-.42.14-1.026.793-1.073l3.456-.233 4.764 7.279v-6.44l-1.215-.14c-.093-.514.28-.886.747-.933l3.222-.187zM2.1 1.155l13.495-.933c1.634-.14 2.055-.047 3.082.7l4.25 2.986c.7.513.933.653.933 1.213v16.378c0 1.026-.373 1.634-1.68 1.726l-15.458.934c-.98.047-1.448-.093-1.962-.747l-3.129-4.06c-.56-.747-.793-1.306-.793-1.96V2.895c0-.84.374-1.54 1.262-1.74z"/>
    </svg>
);

const GitHubIcon = ({ size = 16, className = "" }: { size?: number; className?: string }) => (
    <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="#181717">
        <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0 1 12 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
    </svg>
);

const CalendlyIcon = ({ size = 16, className = "" }: { size?: number; className?: string }) => (
    <svg viewBox="0 0 24 24" width={size} height={size} className={className} fill="#006BFF">
        <path d="M19.655 14.262c.156-.448.24-.925.24-1.424 0-2.398-1.93-4.342-4.31-4.342-1.097 0-2.1.413-2.862 1.093a4.246 4.246 0 0 0-2.861-1.093c-2.38 0-4.31 1.944-4.31 4.342 0 .499.084.976.24 1.424C4.343 14.753 3.347 16.043 3.347 17.5c0 1.934 1.554 3.5 3.47 3.5h10.366c1.916 0 3.47-1.566 3.47-3.5 0-1.457-.996-2.747-2.998-3.238zM12 2c-.69 0-1.25.56-1.25 1.25v2.5c0 .69.56 1.25 1.25 1.25s1.25-.56 1.25-1.25v-2.5C13.25 2.56 12.69 2 12 2z"/>
    </svg>
);

// Map tool names to their icon components
type ToolIconComponent = React.FC<{ size?: number; className?: string }>;

const TOOL_ICON_MAP: Record<string, ToolIconComponent> = {
    // Slack
    slack: SlackIcon,
    send_slack_message: SlackIcon,
    // Google Sheets
    google_sheets: GoogleSheetsIcon,
    log_partnership: GoogleSheetsIcon,
    search_partnerships: GoogleSheetsIcon,
    update_partnership_status: GoogleSheetsIcon,
    // Google Docs
    google_docs: GoogleDocsIcon,
    create_google_doc: GoogleDocsIcon,
    // Notion
    notion: NotionIcon,
    add_timeline_event: NotionIcon,
    query_timeline: NotionIcon,
    // GitHub
    github: GitHubIcon,
    get_repo_stats: GitHubIcon,
    list_issues: GitHubIcon,
    list_pull_requests: GitHubIcon,
    // Calendly
    calendly: CalendlyIcon,
    get_scheduled_events: CalendlyIcon,
    get_user_availability: CalendlyIcon,
};

interface ToolIconProps {
    toolName: string;
    className?: string;
    size?: number;
}

export function ToolIcon({ toolName, className = "", size = 16 }: ToolIconProps) {
    // Normalize tool name to lowercase with underscores
    const normalizedName = toolName.toLowerCase().replace(/\s+/g, '_');

    const IconComponent = TOOL_ICON_MAP[normalizedName];

    if (!IconComponent) {
        // Fallback to generic tool icon
        return <Wrench className={`text-slate-400 ${className}`} style={{ width: size, height: size }} />;
    }

    return <IconComponent size={size} className={className} />;
}

// Get display name for a tool (user-friendly)
export function getToolDisplayName(toolName: string): string {
    const displayNames: Record<string, string> = {
        send_slack_message: "Slack Message",
        log_partnership: "Partnership Log",
        search_partnerships: "Search Partnerships",
        update_partnership_status: "Update Partnership",
        create_google_doc: "Google Doc",
        add_timeline_event: "Notion Timeline",
        query_timeline: "Query Timeline",
        get_repo_stats: "GitHub Stats",
        list_issues: "GitHub Issues",
        list_pull_requests: "GitHub PRs",
        get_scheduled_events: "Calendly Events",
        get_user_availability: "Calendly Availability",
    };

    const normalizedName = toolName.toLowerCase().replace(/\s+/g, '_');
    return displayNames[normalizedName] || toolName.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}
