"use client";

import { useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
    PanelRightClose,
    PanelRight,
} from "lucide-react";

import { Sidebar, ViewType } from "@/components/layout/Sidebar";
import { ChatPanel } from "@/components/agents/ChatPanel";
import { OverviewView } from "@/components/views/OverviewView";
import { PartnershipsView } from "@/components/views/PartnershipsView";
import { FinanceView } from "@/components/views/FinanceView";
import { MarketingView } from "@/components/views/MarketingView";
import { EventsView } from "@/components/views/EventsView";
import { DevelopersView } from "@/components/views/DevelopersView";

export default function Shell() {
    const [activeView, setActiveView] = useState<ViewType>("overview");
    const [isAgentPanelOpen, setIsAgentPanelOpen] = useState(true);

    const renderView = () => {
        switch (activeView) {
            case "overview": return <OverviewView />;
            case "partnerships": return <PartnershipsView />;
            case "finance": return <FinanceView />;
            case "marketing": return <MarketingView />;
            case "events": return <EventsView />;
            case "developers": return <DevelopersView />;
            default: return <OverviewView />;
        }
    };

    return (
        <div className="h-screen w-screen bg-gray-50 overflow-hidden flex">
            {/* Sidebar */}
            <aside className="w-[220px] h-full border-r border-gray-200 flex-shrink-0">
                <Sidebar
                    activeView={activeView}
                    onViewChange={setActiveView}
                />
            </aside>

            {/* Main Content */}
            <main className="flex-1 h-full overflow-hidden flex flex-col">
                {/* Header */}
                <header className="h-14 px-6 flex items-center justify-between border-b border-gray-200 bg-white flex-shrink-0">
                    <nav className="flex items-center gap-2 text-sm">
                        <span className="text-gray-400">Nexus</span>
                        <span className="text-gray-300">/</span>
                        <span className="text-gray-900 font-medium capitalize">{activeView}</span>
                    </nav>

                    <button
                        onClick={() => setIsAgentPanelOpen(!isAgentPanelOpen)}
                        className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors"
                    >
                        {isAgentPanelOpen ? (
                            <>
                                <PanelRightClose className="h-4 w-4" />
                                <span>Hide Agent</span>
                            </>
                        ) : (
                            <>
                                <PanelRight className="h-4 w-4" />
                                <span>Show Agent</span>
                            </>
                        )}
                    </button>
                </header>

                {/* Content */}
                <ScrollArea className="flex-1">
                    <div className="p-6">
                        {renderView()}
                    </div>
                </ScrollArea>
            </main>

            {/* Agent Panel */}
            {isAgentPanelOpen && (
                <aside className="w-[380px] h-full bg-white border-l border-gray-200 flex-shrink-0">
                    <ChatPanel />
                </aside>
            )}
        </div>
    );
}
