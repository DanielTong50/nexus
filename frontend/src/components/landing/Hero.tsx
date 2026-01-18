"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Play, Users, Megaphone, DollarSign, Calendar, Code } from "lucide-react";
import { Button } from "@/components/ui/button";
import { RadialNav } from "@/components/animate-ui/components/community/radial-nav";

const radialNavItems = [
    { id: 1, icon: Users, label: "Partnerships", angle: 0 },
    { id: 2, icon: Megaphone, label: "Marketing", angle: 72 },
    { id: 3, icon: DollarSign, label: "Finance", angle: 144 },
    { id: 4, icon: Calendar, label: "Events", angle: 216 },
    { id: 5, icon: Code, label: "Development", angle: 288 },
];

export function Hero() {
    return (
        <section className="relative min-h-screen flex items-center overflow-hidden pt-16">

            <div className="relative z-10 w-full flex items-center justify-between px-6 sm:px-12 lg:px-24 py-20">
                {/* Left side - Text content */}
                <div className="text-left max-w-xl">

                    {/* Headline */}
                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.1 }}
                        className="text-5xl md:text-6xl lg:text-6xl font-bold text-white tracking-tight"
                    >
                        Deploy the #1
                        <span className="block mt-2 whitespace-nowrap">
                            AI Production Team
                        </span>
                        <span className="block mt-2">
                            for Student Clubs
                        </span>
                    </motion.h1>

                    {/* Subheadline */}
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.2 }}
                        className="mt-6 text-lg md:text-l text-slate-300 max-w-xl leading-relaxed"
                    >
                        Nexus is an AI-native platform that gives student clubs a full production team.
                        From sponsorships to marketing to logistics — all powered by intelligent agents.
                    </motion.p>

                    {/* CTA Buttons */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.3 }}
                        className="mt-10 flex flex-col sm:flex-row items-center justify-start gap-4"
                    >
                        <Link href="/dashboard">
                            <Button size="lg" className="h-12 px-8 text-base bg-white hover:bg-slate-200 text-black shadow-lg">
                                Try it Now!
                                <ArrowRight className="ml-2 h-4 w-4" />
                            </Button>
                        </Link>
                        <Link href="#demo-video">
                            <Button variant="outline" size="lg" className="h-12 px-8 text-base border-slate-600 bg-transparent text-white hover:bg-slate-800 ">
                                <Play className="mr-2 h-4 w-4" />
                                Watch Demo
                            </Button>
                        </Link>
                    </motion.div>

                </div>

                {/* Right side - Radial Nav */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.7, delay: 0.4 }}
                    className="hidden lg:flex items-center justify-center"
                >
                    <RadialNav
                        size={400}
                        items={radialNavItems}
                        defaultActiveId={1}
                        autoRotate={true}
                        autoRotateInterval={1300}
                        menuButtonConfig={{
                            iconSize: 30,
                            buttonSize: 60,
                            buttonPadding: 15,
                        }}
                    />
                </motion.div>
            </div>
        </section>
    );
}
