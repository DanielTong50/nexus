"use client";

import { useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import {
    PanelRight,
    Sparkles,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

import { Sidebar, ViewType } from "@/components/layout/Sidebar";
import { ChatPanel } from "@/components/agents/ChatPanel";
import { PartnershipsView } from "@/components/views/PartnershipsView";
import { FinanceView } from "@/components/views/FinanceView";
import { MarketingView } from "@/components/views/MarketingView";
import { EventsView } from "@/components/views/EventsView";
import { DevelopersView } from "@/components/views/DevelopersView";

export default function Shell() {
    const [activeView, setActiveView] = useState<ViewType>("partnerships");
    const [isAgentPanelOpen, setIsAgentPanelOpen] = useState(true);

    const renderView = () => {
        switch (activeView) {
            case "partnerships": return <PartnershipsView />;
            case "finance": return <FinanceView />;
            case "marketing": return <MarketingView />;
            case "events": return <EventsView />;
            case "developers": return <DevelopersView />;
            default: return <PartnershipsView />;
        }
    };

    return (
        <div className="h-screen w-screen bg-slate-50 overflow-hidden font-sans flex">
            {/* LEFT SIDEBAR - 250px */}
            <aside className="w-[250px] h-full bg-white border-r border-slate-200 flex-shrink-0">
                <Sidebar
                    activeView={activeView}
                    onViewChange={setActiveView}
                />
            </aside>

            {/* MAIN CONTENT AREA - Fluid */}
            <main className="flex-1 h-full overflow-hidden flex flex-col bg-slate-50">
                {/* Top Bar */}
                <header className="h-14 px-10 flex items-center justify-between border-b border-slate-200 bg-white flex-shrink-0">
                    <nav className="flex items-center gap-2 text-sm text-slate-500">
                        <span className="hover:text-slate-900 cursor-pointer">Nexus</span>
                        <span>/</span>
                        <span className="text-slate-900 font-medium capitalize">{activeView}</span>
                    </nav>

                    {!isAgentPanelOpen && (
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setIsAgentPanelOpen(true)}
                            className="text-slate-500 hover:text-slate-900 gap-2"
                        >
                            
                            <span className="text-xs">Open Agent</span>
                        </Button>
                    )}
                </header>

                {/* Content */}
                <ScrollArea className="flex-1">
                    <div className="p-10">
                        {renderView()}
                    </div>
                </ScrollArea>
            </main>

            {/* RIGHT PANEL - Agent Intelligence - 380px */}
            <AnimatePresence>
                {isAgentPanelOpen && (
                    <motion.aside
                        initial={{ width: 0, opacity: 0 }}
                        animate={{ width: 380, opacity: 1 }}
                        exit={{ width: 0, opacity: 0 }}
                        transition={{ duration: 0.15, ease: "easeOut" }}
                        className="h-full bg-white border-l border-slate-200 flex-shrink-0 overflow-hidden"
                    >
                        <div className="w-[380px] h-full">
                            <ChatPanel onClose={() => setIsAgentPanelOpen(false)} />
                        </div>
                    </motion.aside>
                )}
            </AnimatePresence>
        </div>
    );
}
