"use client";

import { useState, useEffect } from "react";
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

// Card component with rotating gradient border
function Card({
    children,
    label,
    delay = 0,
    className = "",
    labelPosition = "bottom",
}: {
    children: React.ReactNode;
    label?: string;
    delay?: number;
    className?: string;
    labelPosition?: "bottom" | "top";
}) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay }}
            className="flex flex-col items-center gap-1.5"
        >
            {label && labelPosition === "top" && (
                <span className="text-[10px] text-white/40 font-medium tracking-wider uppercase">
                    {label}
                </span>
            )}
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
            {label && labelPosition === "bottom" && (
                <span className="text-[10px] text-white/40 font-medium tracking-wider uppercase">
                    {label}
                </span>
            )}
        </motion.div>
    );
}

// Horizontal connector line
function HLine({ width, delay = 0 }: { width: number; delay?: number }) {
    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
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

// Vertical connector line
function VLine({ height, delay = 0 }: { height: number; delay?: number }) {
    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
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

export function WorkflowAnimation() {
    const [aiProviderIndex, setAiProviderIndex] = useState(0);
    const [integrationIndices, setIntegrationIndices] = useState([0, 0, 0, 0]);

    useEffect(() => {
        // AI Engine rotation
        const aiInterval = setInterval(() => {
            setAiProviderIndex((prev) => (prev + 1) % aiProviders.length);
        }, 3000);

        // Staggered intervals for each integration (different timing)
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
        <div className="relative flex flex-col items-center gap-0">
            {/* Step 1: USER */}
            <div className="flex items-center">
                <Card label="User" delay={0.1} className="w-[72px] h-[72px]">
                    <User className="w-9 h-9 text-white" />
                </Card>
            </div>

            {/* Line from User to AI Engine */}
            <VLine height={32} delay={0.2} />

            {/* Step 2: AI ENGINE */}
            <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
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

            {/* Branching lines from AI Engine to Agent AND Database */}
            <div className="flex items-start justify-center">
                <VLine height={24} delay={0.4} />
            </div>
            <div className="flex items-center gap-0">
                <HLine width={80} delay={0.45} />
                <div className="w-[2px] h-[2px] bg-white/15" />
                <HLine width={80} delay={0.45} />
            </div>
            <div className="flex items-start justify-between" style={{ width: 162 }}>
                <VLine height={24} delay={0.5} />
                <VLine height={24} delay={0.5} />
            </div>

            {/* Step 3: AGENT and DATABASE side by side */}
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

            {/* Lines from Agent and Database converging to Integrations */}
            <div className="flex items-start justify-between" style={{ width: 162 }}>
                <VLine height={24} delay={0.65} />
                <VLine height={24} delay={0.65} />
            </div>
            <div className="flex items-center gap-0">
                <HLine width={80} delay={0.7} />
                <div className="w-[2px] h-[2px] bg-white/15" />
                <HLine width={80} delay={0.7} />
            </div>
            <div className="flex items-start justify-center">
                <VLine height={24} delay={0.75} />
            </div>

            {/* Step 4: INTEGRATIONS - All 4 in a container box */}
            <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.8 }}
                className="flex flex-col items-center gap-1.5"
            >
                {/* Outer container box */}
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
    );
}
