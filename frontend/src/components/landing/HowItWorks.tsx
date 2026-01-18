"use client";

import { motion } from "framer-motion";
import { MessageSquare, Bot, CheckCircle, Sparkles } from "lucide-react";

const STEPS = [
    {
        number: "01",
        icon: MessageSquare,
        title: "Tell Nexus What You Need",
        description: "Type a natural language request like 'Draft sponsorship emails for our hackathon' or 'Create a social media calendar for launch week'.",
    },
    {
        number: "02",
        icon: Bot,
        title: "AI Agents Get to Work",
        description: "The right agent team takes over — researching sponsors, drafting content, or updating budgets — all in real-time.",
    },
    {
        number: "03",
        icon: CheckCircle,
        title: "Review and Approve",
        description: "For high-stakes actions, Nexus asks for your approval. Review AI suggestions, make edits, and confirm with one click.",
    },
    {
        number: "04",
        icon: Sparkles,
        title: "Watch Your Event Come to Life",
        description: "Track progress across all teams in one unified dashboard. Your AI team handles the busywork while you focus on the big picture.",
    },
];

export function HowItWorks() {
    return (
        <section id="how-it-works" className="py-24 scroll-mt-20">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5 }}
                    className="text-center mb-16"
                >
                    <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                        How Nexus Works
                    </h2>
                    <p className="text-lg text-slate-400 max-w-2xl mx-auto">
                        From request to execution in four simple steps. No training required.
                    </p>
                </motion.div>

                {/* Steps */}
                <div className="relative">


                    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                        {STEPS.map((step, index) => (
                            <motion.div
                                key={step.number}
                                initial={{ opacity: 0, y: 30 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ duration: 0.5, delay: index * 0.1 }}
                                className="relative h-full"
                            >
                                {/* Step Card */}
                                <div className="h-full bg-slate-900/80 rounded-2xl p-6 border border-slate-700 hover:border-slate-500 hover:shadow-xl transition-all duration-300 relative z-10 flex flex-col">
                                    {/* Number Badge */}
                                    <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center text-black font-bold text-lg mb-4">
                                        {step.number}
                                    </div>

                                    {/* Icon */}
                                    <div className="w-14 h-14 rounded-xl bg-slate-800 flex items-center justify-center mb-4">
                                        <step.icon className="w-7 h-7 text-slate-300" />
                                    </div>

                                    <h3 className="text-xl font-semibold text-white mb-3">
                                        {step.title}
                                    </h3>
                                    <p className="text-slate-400 leading-relaxed">
                                        {step.description}
                                    </p>
                                </div>


                            </motion.div>
                        ))}
                    </div>
                </div>
            </div>
        </section>
    );
}
