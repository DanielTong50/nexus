"use client";

import { useRef, useEffect } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { AgentMessage, Message } from "./AgentMessage";

const MOCK_MESSAGES: Message[] = [
    {
        id: "1",
        role: "user",
        content: "Can you check the sponsorship status for Google and draft a follow-up email?",
    },
    {
        id: "2",
        role: "assistant",
        agentName: "Partnerships",
        content: "I'll check the latest status on Google's sponsorship and prepare a follow-up message for you.",
        isStreaming: false,
        toolCalls: [
            {
                toolName: "search_sponsors",
                status: "success",
                input: 'company="Google"',
                output: JSON.stringify({
                    company: "Google",
                    tier: "Platinum",
                    amount: "$25,000",
                    status: "Confirmed",
                    lastContact: "2 days ago"
                }, null, 2)
            },
            {
                toolName: "draft_email",
                status: "success",
                input: 'type="follow-up"',
                output: "Subject: Spring Gala Partnership - Next Steps\n\nDear Sarah,\n\nThank you for confirming Google's Platinum sponsorship..."
            }
        ]
    },
    {
        id: "3",
        role: "assistant",
        agentName: "Partnerships",
        content: "Google's $25,000 Platinum sponsorship is confirmed. I've drafted a follow-up email for Sarah Chen. Would you like me to send it or make any changes first?",
        isStreaming: false,
    }
];

export function AgentFeed() {
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, []);

    return (
        <ScrollArea className="h-full">
            <div className="flex flex-col p-5">
                {MOCK_MESSAGES.map((msg) => (
                    <AgentMessage key={msg.id} message={msg} />
                ))}
                <div ref={bottomRef} className="h-4" />
            </div>
        </ScrollArea>
    );
}
