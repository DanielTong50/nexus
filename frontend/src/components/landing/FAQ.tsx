"use client";

import { motion } from "framer-motion";
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "@/components/ui/accordion";

const FAQS = [
    {
        question: "What is Nexus?",
        answer: "Nexus is an AI-native event production platform designed for student organizations. It provides five specialized AI agent teams that handle partnerships, marketing, finance, events, and development tasks, allowing your club to operate like a full production team.",
    },
    {
        question: "How do the AI agents work?",
        answer: "You interact with Nexus through natural language — just type what you need, like 'Draft a sponsorship email to Acme Corp' or 'Create a social media post for our launch'. The appropriate AI agent takes over, researches context, drafts content, and presents it for your approval before taking action.",
    },
    {
        question: "Is Nexus free for student organizations?",
        answer: "Yes! Nexus offers a generous free tier for qualifying student organizations. We believe in supporting the student community and making professional-grade tools accessible to clubs of all sizes.",
    },
    {
        question: "What is Human-in-the-Loop (HITL)?",
        answer: "HITL means AI agents ask for your approval before taking high-stakes actions like sending emails, making payments, or publishing content. You always stay in control — the AI handles the grunt work, but you make the final call on important decisions.",
    },
    {
        question: "Can multiple team members use Nexus?",
        answer: "Nexus supports full team collaboration. Multiple team members can interact with the AI agents simultaneously, and everyone can see the work being done in real-time on the unified dashboard.",
    },
    {
        question: "What integrations does Nexus support?",
        answer: "Nexus integrates with popular tools including Gmail for email outreach, Google Sheets for sponsor tracking, Notion for documentation, Stripe for payments, and GitHub for development teams. We're constantly adding new integrations based on user feedback.",
    },
    {
        question: "How secure is my data?",
        answer: "Security is a top priority. All data is encrypted in transit and at rest. We use industry-standard security practices and never share your data with third parties. Your sponsor lists, financial data, and communications remain completely private.",
    },
    {
        question: "Can I customize the AI agents?",
        answer: "Yes! You can train agents with your organization's specific context, templates, and preferences. The more you use Nexus, the better it understands your club's voice and needs.",
    },
];

export function FAQ() {
    return (
        <section id="faq" className="py-24 scroll-mt-20">
            <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5 }}
                    className="text-center mb-12"
                >
                    <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                        Frequently Asked Questions
                    </h2>
                    <p className="text-lg text-slate-400">
                        Everything you need to know about Nexus
                    </p>
                </motion.div>

                {/* FAQ Accordion */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: 0.1 }}
                >
                    <Accordion type="single" collapsible className="space-y-4">
                        {FAQS.map((faq, index) => (
                            <AccordionItem
                                key={index}
                                value={`item-${index}`}
                                className="border border-slate-700 rounded-lg px-6 data-[state=open]:bg-slate-900/50 transition-colors"
                            >
                                <AccordionTrigger className="text-left font-medium text-white hover:no-underline py-4">
                                    {faq.question}
                                </AccordionTrigger>
                                <AccordionContent className="text-slate-400 pb-4">
                                    {faq.answer}
                                </AccordionContent>
                            </AccordionItem>
                        ))}
                    </Accordion>
                </motion.div>
            </div>
        </section>
    );
}
