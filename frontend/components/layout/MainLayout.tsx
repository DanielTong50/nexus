"use client";

import { useState } from "react";
import { Navbar } from "./Navbar";
import { ChatPanel } from "./ChatPanel";
import { cn } from "@/lib/utils";

interface MainLayoutProps {
    children: React.ReactNode;
}

/**
 * Main layout wrapper with flex container for navbar + content.
 * Manages chat panel open/close state.
 */
export function MainLayout({ children }: MainLayoutProps): React.ReactElement {
    const [chatOpen, setChatOpen] = useState(false);

    const toggleChat = (): void => {
        setChatOpen((prev) => !prev);
    };

    return (
        <div className="flex h-screen overflow-hidden">
            {/* Left Navbar */}
            <Navbar collapsed={chatOpen} />

            {/* Chat Panel - 25% width when open */}
            {chatOpen && (
                <ChatPanel
                    isOpen={chatOpen}
                    onClose={() => setChatOpen(false)}
                    eventId=""
                />
            )}

            {/* Main Content - Remaining width */}
            <main className={cn(
                "flex-1 overflow-auto bg-background",
                "transition-all duration-300"
            )}>
                {/* Chat Toggle Button */}
                <button
                    onClick={toggleChat}
                    className={cn(
                        "fixed bottom-6 right-6 z-50",
                        "w-14 h-14 rounded-full",
                        "bg-accent text-white shadow-lg",
                        "flex items-center justify-center",
                        "hover:bg-blue-600 transition-colors duration-200",
                        "focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2"
                    )}
                    aria-label={chatOpen ? "Close chat" : "Open chat"}
                >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        {chatOpen ? (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        ) : (
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                        )}
                    </svg>
                </button>

                {/* Page Content */}
                <div className="p-6">
                    {children}
                </div>
            </main>
        </div>
    );
}
