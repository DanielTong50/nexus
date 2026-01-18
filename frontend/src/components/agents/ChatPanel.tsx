"use client";

import { useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { AlertCircle, Trash2, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useAgentStream } from "@/hooks/useAgentStream";
import { AgentProgressCard } from "./AgentProgressCard";
import { ChatInput } from "./ChatInput";
import type { UserMessage } from "./types";

interface ChatPanelProps {
    onClose?: () => void;
}

// Integration logo icons - Modern Slack logo with multiple colors
const SlackLogo = ({ size = 24 }: { size?: number }) => (
    <svg viewBox="0 0 24 24" width={size} height={size}>
        <path fill="#E01E5A" d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zm1.271 0a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313z"/>
        <path fill="#36C5F0" d="M8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zm0 1.271a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312z"/>
        <path fill="#2EB67D" d="M18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zm-1.27 0a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.165 0a2.528 2.528 0 0 1 2.523 2.522v6.312z"/>
        <path fill="#ECB22E" d="M15.165 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.165 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52zm0-1.27a2.527 2.527 0 0 1-2.52-2.523 2.526 2.526 0 0 1 2.52-2.52h6.313A2.527 2.527 0 0 1 24 15.165a2.528 2.528 0 0 1-2.522 2.523h-6.313z"/>
    </svg>
);

const GoogleDocsLogo = ({ size = 24 }: { size?: number }) => (
    <svg viewBox="0 0 24 24" width={size} height={size} fill="#4285F4">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zm-1 2l5 5h-5V4zM6 20V4h6v6h6v10H6zm2-6h8v2H8v-2zm0-4h8v2H8v-2zm0 8h5v2H8v-2z"/>
    </svg>
);

const GitHubLogo = ({ size = 24 }: { size?: number }) => (
    <svg viewBox="0 0 24 24" width={size} height={size} fill="#181717">
        <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0 1 12 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
    </svg>
);

const GoogleSheetsLogo = ({ size = 24 }: { size?: number }) => (
    <svg viewBox="0 0 24 24" width={size} height={size} fill="#34A853">
        <path d="M19.385 2H4.615A2.615 2.615 0 0 0 2 4.615v14.77A2.615 2.615 0 0 0 4.615 22h14.77A2.615 2.615 0 0 0 22 19.385V4.615A2.615 2.615 0 0 0 19.385 2zM8 17H6v-2h2v2zm0-4H6v-2h2v2zm0-4H6V7h2v2zm4 8h-2v-2h2v2zm0-4h-2v-2h2v2zm0-4h-2V7h2v2zm6 8h-4v-2h4v2zm0-4h-4v-2h4v2zm0-4h-4V7h4v2z"/>
    </svg>
);

const NotionLogo = ({ size = 24 }: { size?: number }) => (
    <svg viewBox="0 0 24 24" width={size} height={size} fill="#000000">
        <path d="M4.459 4.208c.746.606 1.026.56 2.428.466l13.215-.793c.28 0 .047-.28-.046-.326L17.86 1.968c-.42-.326-.98-.7-2.055-.607L3.01 2.295c-.466.046-.56.28-.374.466l1.823 1.447zm.793 3.08v13.904c0 .747.373 1.027 1.214.98l14.523-.84c.841-.046.934-.56.934-1.167V6.354c0-.606-.233-.933-.747-.886l-15.177.887c-.56.047-.747.327-.747.933zm14.337.745c.093.42 0 .84-.42.888l-.7.14v10.264c-.608.327-1.168.514-1.635.514-.747 0-.934-.234-1.495-.933l-4.577-7.186v6.952l1.448.327s0 .84-1.168.84l-3.22.186c-.093-.186 0-.653.327-.746l.84-.233V9.854L7.822 9.76c-.094-.42.14-1.026.793-1.073l3.456-.233 4.764 7.279v-6.44l-1.215-.14c-.093-.514.28-.886.747-.933l3.222-.187zM2.1 1.155l13.495-.933c1.634-.14 2.055-.047 3.082.7l4.25 2.986c.7.513.933.653.933 1.213v16.378c0 1.026-.373 1.634-1.68 1.726l-15.458.934c-.98.047-1.448-.093-1.962-.747l-3.129-4.06c-.56-.747-.793-1.306-.793-1.96V2.895c0-.84.374-1.54 1.262-1.74z"/>
    </svg>
);

const CalendlyLogo = ({ size = 24 }: { size?: number }) => (
    <svg viewBox="0 0 24 24" width={size} height={size} fill="#006BFF">
        <path d="M19.655 14.262c.156-.448.24-.925.24-1.424 0-2.398-1.93-4.342-4.31-4.342-1.097 0-2.1.413-2.862 1.093a4.246 4.246 0 0 0-2.861-1.093c-2.38 0-4.31 1.944-4.31 4.342 0 .499.084.976.24 1.424C4.343 14.753 3.347 16.043 3.347 17.5c0 1.934 1.554 3.5 3.47 3.5h10.366c1.916 0 3.47-1.566 3.47-3.5 0-1.457-.996-2.747-2.998-3.238zM12 2c-.69 0-1.25.56-1.25 1.25v2.5c0 .69.56 1.25 1.25 1.25s1.25-.56 1.25-1.25v-2.5C13.25 2.56 12.69 2 12 2z"/>
    </svg>
);

const GmailLogo = ({ size = 24 }: { size?: number }) => (
    <svg viewBox="0 0 24 24" width={size} height={size}>
        <path fill="#4285F4" d="M2 6.5V18c0 1.1.9 2 2 2h1V6.2L12 11l7-4.8V20h1c1.1 0 2-.9 2-2V6.5l-1.5-1.4L12 11 3.5 5.1 2 6.5z"/>
        <path fill="#EA4335" d="M22 6.5V6c0-.8-.5-1.5-1.2-1.8L12 9.5 3.2 4.2C2.5 4.5 2 5.2 2 6v.5l10 6.5 10-6.5z"/>
        <path fill="#FBBC05" d="M5 20V6.2l7 4.8V20H5z"/>
        <path fill="#34A853" d="M19 20h-7v-9l7 4.8V20z"/>
    </svg>
);

const DiscordLogo = ({ size = 24 }: { size?: number }) => (
    <svg viewBox="0 0 24 24" width={size} height={size} fill="#5865F2">
        <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
    </svg>
);

const JiraLogo = ({ size = 24 }: { size?: number }) => (
    <svg viewBox="0 0 24 24" width={size} height={size}>
        <defs>
            <linearGradient id="jira-gradient-1" x1="99.68%" y1="15.8%" x2="24.96%" y2="62.92%">
                <stop offset="18%" stopColor="#0052CC"/>
                <stop offset="100%" stopColor="#2684FF"/>
            </linearGradient>
            <linearGradient id="jira-gradient-2" x1="0.59%" y1="84.78%" x2="75.42%" y2="37.52%">
                <stop offset="18%" stopColor="#0052CC"/>
                <stop offset="100%" stopColor="#2684FF"/>
            </linearGradient>
        </defs>
        <path fill="url(#jira-gradient-1)" d="M12.005 0L5.197 6.808l6.808 6.808 6.808-6.808L12.005 0zM5.197 6.808L0 12.005l6.808 6.808 6.808-6.808-6.808-6.808-.811.803z"/>
        <path fill="url(#jira-gradient-2)" d="M12.005 12.005L5.197 18.813 12.005 24l6.808-6.808-6.808-6.808v-.379z"/>
    </svg>
);

// Floating bubble component
interface FloatingBubbleProps {
    children: React.ReactNode;
    initialX: number;
    initialY: number;
    delay: number;
    duration: number;
    size?: "sm" | "md";
}

function FloatingBubble({ children, initialX, initialY, delay, duration, size = "md" }: FloatingBubbleProps) {
    const sizeClass = size === "sm" ? "w-8 h-8" : "w-10 h-10";
    return (
        <motion.div
            className={`absolute ${sizeClass} rounded-xl bg-white shadow-sm border border-slate-100 flex items-center justify-center opacity-60`}
            initial={{ x: initialX, y: initialY }}
            animate={{
                x: [initialX, initialX + 8, initialX - 5, initialX + 3, initialX],
                y: [initialY, initialY - 10, initialY + 5, initialY - 8, initialY],
            }}
            transition={{
                duration: duration,
                delay: delay,
                repeat: Infinity,
                repeatType: "reverse",
                ease: "easeInOut",
            }}
        >
            {children}
        </motion.div>
    );
}

// User message component
function UserMessageBubble({ message }: { message: UserMessage }) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-end"
        >
            <div className="max-w-[85%] px-4 py-2.5 rounded-2xl rounded-br-md border border-slate-200 text-slate-700">
                <p className="text-sm leading-relaxed">{message.content}</p>
            </div>
        </motion.div>
    );
}

export function ChatPanel({ onClose }: ChatPanelProps) {
    const { feedItems, isStreaming, error, sendMessage, clearMessages } = useAgentStream();
    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when messages change
    useEffect(() => {
        if (scrollRef.current) {
            const scrollContainer = scrollRef.current.querySelector('[data-radix-scroll-area-viewport]');
            if (scrollContainer) {
                scrollContainer.scrollTop = scrollContainer.scrollHeight;
            }
        }
    }, [feedItems]);

    const handleSendMessage = async (message: string) => {
        await sendMessage(message);
    };

    return (
        <div className="flex flex-col h-full bg-slate-50">
            {/* Header */}
            <header className="h-14 px-5 flex items-center justify-between border-b border-slate-200 bg-white flex-shrink-0">
                <div className="flex items-center gap-3">
                    {onClose && (
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={onClose}
                            className="h-7 w-7 p-0 text-slate-400 hover:text-slate-600"
                            title="Close panel"
                        >
                            <X className="h-4 w-4" />
                        </Button>
                    )}
                    <span className="text-sm font-semibold text-slate-900">Agent Intelligence</span>
                </div>
                <div className="flex items-center gap-3">
                    {error && (
                        <div className="flex items-center gap-1 text-red-500">
                            <AlertCircle className="h-3.5 w-3.5" />
                            <span className="text-xs font-medium">Error</span>
                        </div>
                    )}
                    {isStreaming && (
                        <div className="flex items-center gap-1.5">
                            <div className="h-2 w-2 rounded-full bg-amber-500 animate-pulse" />
                            <span className="text-xs text-slate-500">Processing...</span>
                        </div>
                    )}
                    {feedItems.length > 0 && (
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={clearMessages}
                            className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors"
                            title="Clear chat"
                        >
                            <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                    )}
                </div>
            </header>

            {/* Messages Feed */}
            <ScrollArea className="flex-1" ref={scrollRef}>
                <div className="p-5 space-y-4">
                    {feedItems.length === 0 ? (
                        <div className="text-center py-12">
                            {/* Floating bubbles with integration logos - random scattered arrangement */}
                            <div className="relative w-72 h-48 mx-auto mb-4">
                                {/* Randomly scattered bubbles */}
                                <FloatingBubble initialX={45} initialY={8} delay={0} duration={4.2}>
                                    <SlackLogo size={20} />
                                </FloatingBubble>
                                <FloatingBubble initialX={180} initialY={22} delay={0.7} duration={3.6}>
                                    <GmailLogo size={20} />
                                </FloatingBubble>
                                <FloatingBubble initialX={115} initialY={55} delay={0.3} duration={4.8}>
                                    <GitHubLogo size={20} />
                                </FloatingBubble>
                                <FloatingBubble initialX={8} initialY={72} delay={1.1} duration={3.9}>
                                    <DiscordLogo size={20} />
                                </FloatingBubble>
                                <FloatingBubble initialX={220} initialY={95} delay={0.5} duration={4.4}>
                                    <JiraLogo size={20} />
                                </FloatingBubble>
                                <FloatingBubble initialX={160} initialY={118} delay={0.2} duration={3.7}>
                                    <NotionLogo size={20} />
                                </FloatingBubble>
                                <FloatingBubble initialX={70} initialY={135} delay={0.9} duration={4.1}>
                                    <GoogleDocsLogo size={20} />
                                </FloatingBubble>
                                <FloatingBubble initialX={240} initialY={45} delay={0.4} duration={4.5}>
                                    <CalendlyLogo size={20} />
                                </FloatingBubble>
                                <FloatingBubble initialX={25} initialY={115} delay={0.8} duration={3.5}>
                                    <GoogleSheetsLogo size={20} />
                                </FloatingBubble>
                            </div>

                            <p className="text-sm font-normal text-slate-400 mb-10">
                                Integrated Every Feature – <span className="text-blue-500 font-medium">powered by Vultr</span>
                            </p>
                        </div>
                    ) : (
                        <AnimatePresence mode="popLayout">
                            {feedItems.map((item) => (
                                <motion.div
                                    key={item.type === 'user' ? item.data.id : item.data.id}
                                    layout
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -10 }}
                                    transition={{ duration: 0.2 }}
                                >
                                    {item.type === 'user' ? (
                                        <UserMessageBubble message={item.data} />
                                    ) : (
                                        <AgentProgressCard task={item.data} />
                                    )}
                                </motion.div>
                            ))}
                        </AnimatePresence>
                    )}
                </div>
            </ScrollArea>

            {/* Input Area */}
            <ChatInput
                onSubmit={handleSendMessage}
                isLoading={isStreaming}
                placeholder="Ask the agent anything..."
            />
        </div>
    );
}
