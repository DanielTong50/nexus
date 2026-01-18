"use client";

import type React from "react";
import { useState } from "react";
import "./globals.css";
import { Navbar } from "@/components/layout/Navbar";
import { cn } from "@/lib/utils";

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>): React.ReactElement {
    const [chatOpen, setChatOpen] = useState(false);

    return (
        <html lang="en">
            <body className="bg-background text-primary">
                <div className="flex h-screen overflow-hidden">
                    {/* Left Navbar */}
                    <Navbar collapsed={chatOpen} />

                    {/* Main Content */}
                    <main className="flex-1 overflow-auto">
                        {children}
                    </main>

                    {/* Chat Toggle Button */}
                    <button
                        onClick={() => setChatOpen(!chatOpen)}
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
                </div>
            </body>
        </html>
    );
}
