"use client";

import { useRef, useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { User, Bot } from "lucide-react";
import Image from "next/image";

// Each integration box rotates between 2 unique icons (8 total, no repeats)
const integrationSets = [
    ["/photos/slack.png", "/photos/googlemeet.png"],
    ["/photos/discord.png", "/photos/microsoftteams.png"],
    ["/photos/notion.png", "/photos/figma.png"],
    ["/photos/googlesheets.png", "/photos/excel.png"],
];

// AI Engine rotates between these
const aiProviders = [
    { name: "Gemini", icon: "/photos/gemini.png" },
    { name: "Vultr", icon: "/photos/vultr.webp" },
];

const STEPS = [
    {
        number: "01",
        title: "Tell Nexus What You Need",
        description: "Provide a single natural language update, like \"Just finished a meeting with Google; they’re sponsoring $1,000 for Blueprint\". Our Classifier and Router nodes immediately parse your intent to trigger the appropriate workflows.",
    },
    {
        number: "02",
        title: "AI Agents Get to Work",
        description: "Specialized agents for Partnerships, Marketing, Finance, Events, and Developers execute tasks in parallel using asyncio. They simultaneously search documents, draft outreach, and update logistics without any manual intervention.",
    },
    {
        number: "03",
        title: "Review and Approve",
        description: "For actions that impact sponsors, finances, or public-facing content, Nexus keeps humans in the loop. Generated outputs, such as MOUs, invoices, emails, or announcements are queued for review before execution. You maintain full control by reviewing, editing, and confirming AI-generated actions before they are finalized.",
    },
    {
        number: "04",
        title: "Watch It Come to Life",
        description: "Approved actions are instantly synced across your entire ecosystem, from Google Sheets and Slack to GitHub and Figma. Our extensible architecture is designed to scale across 30+ productivity tools, unifying your fragmented club operations into one command center.",
    },
];

// Card component with rotating gradient border
function Card({
    children,
    label,
    delay = 0,
    className = "",
}: {
    children: React.ReactNode;
    label?: string;
    delay?: number;
    className?: string;
}) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 15 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay }}
            className="flex flex-col items-center gap-1.5"
        >
            <div className={`relative ${className}`}>
                <div className="absolute top-1.5 left-1 w-full h-full rounded-xl bg-neutral-800 border border-white/10" />
                <div className="relative w-full h-full rounded-xl bg-neutral-900 border border-white/20 flex items-center justify-center overflow-hidden">
                    <motion.div
                        className="absolute -inset-[50%] origin-center"
                        style={{
                            background: "conic-gradient(from 0deg, transparent 0%, rgba(255,255,255,0.6) 10%, transparent 20%, transparent 100%)",
                        }}
                        animate={{ rotate: 360 }}
                        transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                    />
                    <div className="absolute inset-[1px] rounded-[10px] bg-neutral-900" />
                    <div className="relative z-10">{children}</div>
                </div>
            </div>
            {label && (
                <span className="text-[10px] text-white/40 font-medium tracking-wider uppercase">
                    {label}
                </span>
            )}
        </motion.div>
    );
}

// Vertical connector line
function VLine({ height, delay = 0 }: { height: number; delay?: number }) {
    return (
        <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.3, delay }}
            className="relative overflow-hidden"
            style={{ width: 2, height }}
        >
            <div className="absolute inset-0 bg-white/15" />
            <motion.div
                className="absolute w-full h-4"
                style={{ background: "linear-gradient(180deg, transparent, rgba(255,255,255,0.8), transparent)" }}
                animate={{ y: [-16, height] }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
            />
        </motion.div>
    );
}

// Horizontal connector line
function HLine({ width, delay = 0 }: { width: number; delay?: number }) {
    return (
        <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.3, delay }}
            className="relative overflow-hidden"
            style={{ width, height: 2 }}
        >
            <div className="absolute inset-0 bg-white/15" />
            <motion.div
                className="absolute h-full w-4"
                style={{ background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent)" }}
                animate={{ x: [-16, width] }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
            />
        </motion.div>
    );
}

// Step text component
function StepText({ step, isActive }: { step: typeof STEPS[0]; isActive: boolean }) {
    return (
        <div className="flex items-start gap-4 max-w-xl">
            <span
                className={`text-3xl font-bold transition-all duration-500 flex-shrink-0 ${isActive ? "text-white" : "text-white/20"
                    }`}
            >
                {step.number}
            </span>
            <div className="flex flex-col min-w-0">
                <h3
                    className={`text-base font-bold transition-all duration-500 ${isActive ? "text-white" : "text-white/30"
                        }`}
                >
                    {step.title}
                </h3>
                <p
                    className={`text-xs transition-all duration-500 ${isActive ? "text-slate-400" : "text-slate-500/50"
                        }`}
                >
                    {step.description}
                </p>
            </div>
        </div>
    );
}

export function HowItWorks() {
    const containerRef = useRef<HTMLDivElement>(null);
    const [activeStep, setActiveStep] = useState(0);
    const [aiProviderIndex, setAiProviderIndex] = useState(0);
    const [integrationIndices, setIntegrationIndices] = useState([0, 0, 0, 0]);

    useEffect(() => {
        const handleScroll = () => {
            if (!containerRef.current) return;

            const container = containerRef.current;
            const rect = container.getBoundingClientRect();
            const viewportHeight = window.innerHeight;

            // Track scroll from when section enters viewport to when it leaves
            // This creates a much larger scroll range for step progression
            const sectionTop = rect.top;
            const sectionBottom = rect.bottom;

            // Start tracking when section top reaches 80% of viewport
            const startThreshold = viewportHeight * 0.8;
            // End tracking when section bottom reaches 20% of viewport
            const endThreshold = viewportHeight * 0.2;

            // Total scroll distance = from section entering to section leaving
            const totalScrollRange = (rect.height + viewportHeight * 0.6);
            const scrolledAmount = startThreshold - sectionTop;

            const scrollProgress = Math.max(0, Math.min(1,
                scrolledAmount / totalScrollRange
            ));

            // Map progress to step index (0-3)
            const stepIndex = Math.min(3, Math.floor(scrollProgress * 4));
            setActiveStep(stepIndex);
        };

        window.addEventListener("scroll", handleScroll);
        handleScroll();

        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    useEffect(() => {
        // AI Engine rotation
        const aiInterval = setInterval(() => {
            setAiProviderIndex((prev) => (prev + 1) % aiProviders.length);
        }, 3000);

        // Staggered intervals for each integration
        const intervals = [2400, 3100, 2700, 3500];
        const intIntervals = intervals.map((interval, idx) =>
            setInterval(() => {
                setIntegrationIndices((prev) => {
                    const newIndices = [...prev];
                    newIndices[idx] = (newIndices[idx] + 1) % 2;
                    return newIndices;
                });
            }, interval)
        );

        return () => {
            clearInterval(aiInterval);
            intIntervals.forEach(clearInterval);
        };
    }, []);

    return (
        <section id="how-it-works" className="bg-black scroll-mt-20" ref={containerRef}>
            <div className="px-6 sm:px-12 lg:px-24">
                {/* Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5 }}
                    className="text-center py-16"
                >
                    <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                        How Nexus Works
                    </h2>
                    <p className="text-lg text-slate-400 max-w-2xl mx-auto">
                        Our agentic flow turns your request into three simple steps. No training required, all integrated for you.
                    </p>
                </motion.div>

                {/* Main Content */}
                <div className="rounded-2xl border border-white/15 bg-neutral-900/30 overflow-hidden">
                    <div className="flex flex-col lg:flex-row">
                        {/* Left: Sticky Workflow Column */}
                        <div className="flex-shrink-0 lg:sticky lg:top-20 lg:self-start p-8 lg:p-10">
                            <div className="flex flex-col items-center">
                                {/* Row 1: User */}
                                <div className="h-[100px] flex items-center">
                                    <Card label="User" delay={0.1} className="w-[72px] h-[72px]">
                                        <User className="w-9 h-9 text-white" />
                                    </Card>
                                </div>

                                {/* Connector */}
                                <VLine height={40} delay={0.2} />

                                {/* Row 2: AI Engine */}
                                <div className="h-[110px] flex items-center">
                                    <motion.div
                                        initial={{ opacity: 0, y: 15 }}
                                        whileInView={{ opacity: 1, y: 0 }}
                                        viewport={{ once: true }}
                                        transition={{ duration: 0.5, delay: 0.3 }}
                                        className="flex flex-col items-center gap-1.5"
                                    >
                                        <div className="relative w-[80px] h-[80px]">
                                            <div className="absolute top-1.5 left-1 w-full h-full rounded-xl bg-neutral-800 border border-white/10" />
                                            <div className="relative w-full h-full rounded-xl bg-neutral-900 border border-white/20 flex items-center justify-center overflow-hidden">
                                                <motion.div
                                                    className="absolute -inset-[50%] origin-center"
                                                    style={{ background: "conic-gradient(from 0deg, transparent 0%, rgba(255,255,255,0.6) 10%, transparent 20%, transparent 100%)" }}
                                                    animate={{ rotate: 360 }}
                                                    transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                                                />
                                                <div className="absolute inset-[1px] rounded-[10px] bg-neutral-900" />
                                                <AnimatePresence mode="wait">
                                                    <motion.div
                                                        key={aiProviderIndex}
                                                        initial={{ opacity: 0, scale: 0.8 }}
                                                        animate={{ opacity: 1, scale: 1 }}
                                                        exit={{ opacity: 0, scale: 0.8 }}
                                                        transition={{ duration: 0.4 }}
                                                        className="relative z-10"
                                                    >
                                                        <Image
                                                            src={aiProviders[aiProviderIndex].icon}
                                                            alt={aiProviders[aiProviderIndex].name}
                                                            width={52}
                                                            height={52}
                                                            className="w-13 h-13 object-contain"
                                                        />
                                                    </motion.div>
                                                </AnimatePresence>
                                            </div>
                                        </div>
                                        <span className="text-[10px] text-white/40 font-medium tracking-wider uppercase">AI Engine</span>
                                    </motion.div>
                                </div>

                                {/* Branching connector */}
                                <VLine height={24} delay={0.4} />
                                <div className="flex items-center gap-0">
                                    <HLine width={80} delay={0.45} />
                                    <div className="w-[2px] h-[2px] bg-white/15" />
                                    <HLine width={80} delay={0.45} />
                                </div>
                                <div className="flex items-start justify-between" style={{ width: 162 }}>
                                    <VLine height={24} delay={0.5} />
                                    <VLine height={24} delay={0.5} />
                                </div>

                                {/* Row 3: Agent + Database */}
                                <div className="h-[110px] flex items-center">
                                    <div className="flex items-start gap-8">
                                        <Card label="Agent" delay={0.55} className="w-[72px] h-[72px]">
                                            <Bot className="w-9 h-9 text-white" />
                                        </Card>
                                        <Card label="Database" delay={0.55} className="w-[72px] h-[72px]">
                                            <Image
                                                src="/photos/mongo_db_circle.svg"
                                                alt="MongoDB"
                                                width={48}
                                                height={48}
                                                className="w-12 h-12 object-contain"
                                            />
                                        </Card>
                                    </div>
                                </div>

                                {/* Converging connector */}
                                <div className="flex items-start justify-between" style={{ width: 162 }}>
                                    <VLine height={24} delay={0.65} />
                                    <VLine height={24} delay={0.65} />
                                </div>
                                <div className="flex items-center gap-0">
                                    <HLine width={80} delay={0.7} />
                                    <div className="w-[2px] h-[2px] bg-white/15" />
                                    <HLine width={80} delay={0.7} />
                                </div>
                                <VLine height={24} delay={0.75} />

                                {/* Row 4: Integrations */}
                                <div className="h-[110px] flex items-center">
                                    <motion.div
                                        initial={{ opacity: 0, y: 15 }}
                                        whileInView={{ opacity: 1, y: 0 }}
                                        viewport={{ once: true }}
                                        transition={{ duration: 0.5, delay: 0.8 }}
                                        className="flex flex-col items-center gap-1.5"
                                    >
                                        <div className="relative p-4 rounded-2xl border border-white/15 bg-neutral-900/50">
                                            <div className="absolute inset-0 rounded-2xl bg-gradient-to-b from-white/5 to-transparent" />
                                            <div className="relative flex items-center gap-3">
                                                {[0, 1, 2, 3].map((boxIndex) => (
                                                    <div key={boxIndex} className="relative w-[60px] h-[60px]">
                                                        <div className="absolute top-1 left-0.5 w-full h-full rounded-lg bg-neutral-800 border border-white/10" />
                                                        <div className="relative w-full h-full rounded-lg bg-neutral-900 border border-white/20 flex items-center justify-center overflow-hidden">
                                                            <motion.div
                                                                className="absolute -inset-[50%] origin-center"
                                                                style={{ background: "conic-gradient(from 0deg, transparent 0%, rgba(255,255,255,0.5) 10%, transparent 20%, transparent 100%)" }}
                                                                animate={{ rotate: 360 }}
                                                                transition={{ duration: 3, repeat: Infinity, ease: "linear", delay: boxIndex * 0.2 }}
                                                            />
                                                            <div className="absolute inset-[1px] rounded-[6px] bg-neutral-900" />
                                                            <AnimatePresence mode="wait">
                                                                <motion.div
                                                                    key={integrationIndices[boxIndex]}
                                                                    initial={{ y: 15, opacity: 0 }}
                                                                    animate={{ y: 0, opacity: 1 }}
                                                                    exit={{ y: -15, opacity: 0 }}
                                                                    transition={{ duration: 0.3 }}
                                                                    className="relative z-10"
                                                                >
                                                                    <Image
                                                                        src={integrationSets[boxIndex][integrationIndices[boxIndex]]}
                                                                        alt="Integration"
                                                                        width={36}
                                                                        height={36}
                                                                        className="w-9 h-9 object-contain"
                                                                    />
                                                                </motion.div>
                                                            </AnimatePresence>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                        <span className="text-[10px] text-white/40 font-medium tracking-wider uppercase">Integrations</span>
                                    </motion.div>
                                </div>
                            </div>
                        </div>

                        {/* Divider */}
                        <div className="hidden lg:block w-px bg-white/15" />
                        <div className="lg:hidden h-px bg-white/15 mx-8" />

                        {/* Right: Aligned Steps */}
                        <div className="flex-1 p-8 lg:p-10">
                            <div className="flex flex-col">
                                {/* Row 1: User step */}
                                <div className="h-[100px] flex items-center">
                                    <StepText step={STEPS[0]} isActive={activeStep === 0} />
                                </div>

                                {/* Spacer for connector */}
                                <div className="h-[40px]" />

                                {/* Row 2: AI Engine step */}
                                <div className="h-[110px] flex items-center">
                                    <StepText step={STEPS[1]} isActive={activeStep === 1} />
                                </div>

                                {/* Spacer for branching connector */}
                                <div className="h-[74px]" />

                                {/* Row 3: Agent/Database step */}
                                <div className="h-[110px] flex items-center">
                                    <StepText step={STEPS[2]} isActive={activeStep === 2} />
                                </div>

                                {/* Spacer for converging connector */}
                                <div className="h-[74px]" />

                                {/* Row 4: Integrations step */}
                                <div className="h-[110px] flex items-center">
                                    <StepText step={STEPS[3]} isActive={activeStep === 3} />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
