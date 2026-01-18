"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Play, Sparkles, Zap, Bot, Calendar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const floatingIcons = [
    { Icon: Bot, delay: 0, x: "10%", y: "20%" },
    { Icon: Calendar, delay: 0.2, x: "85%", y: "15%" },
    { Icon: Zap, delay: 0.4, x: "15%", y: "70%" },
    { Icon: Sparkles, delay: 0.6, x: "80%", y: "75%" },
];

export function Hero() {
    return (
        <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-white pt-16">
            {/* Animated Background Grid */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#e5e7eb_1px,transparent_1px),linear-gradient(to_bottom,#e5e7eb_1px,transparent_1px)] bg-[size:64px_64px]" />

            {/* Gradient Orbs - subtle gray */}
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-slate-100 rounded-full blur-3xl opacity-50" />
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-slate-200 rounded-full blur-3xl opacity-50" />

            {/* Floating Icons */}
            {floatingIcons.map(({ Icon, delay, x, y }, index) => (
                <motion.div
                    key={index}
                    className="absolute text-slate-300"
                    style={{ left: x, top: y }}
                    initial={{ y: 0, opacity: 0 }}
                    animate={{ y: [0, -20, 0], opacity: 0.3 }}
                    transition={{
                        y: { duration: 3, repeat: Infinity, ease: "easeInOut" },
                        opacity: { duration: 0.5, delay },
                    }}
                >
                    <Icon className="w-12 h-12" />
                </motion.div>
            ))}

            <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
                <div className="text-center">
                    {/* Badge */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                    >
                        <Badge variant="outline" className="mb-6 px-4 py-1.5 text-sm font-medium bg-white border-slate-300 text-slate-700">
                            <Sparkles className="w-3.5 h-3.5 mr-1.5" />
                            AI-Powered Event Production
                        </Badge>
                    </motion.div>

                    {/* Headline */}
                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.1 }}
                        className="text-5xl md:text-6xl lg:text-7xl font-bold text-slate-900 tracking-tight"
                    >
                        Run Events Like a
                        <span className="block mt-2">
                            10x Team
                        </span>
                    </motion.h1>

                    {/* Subheadline */}
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.2 }}
                        className="mt-6 text-xl md:text-2xl text-slate-600 max-w-3xl mx-auto leading-relaxed"
                    >
                        Nexus is an AI-native platform that gives student clubs a full production team.
                        From sponsorships to marketing to logistics — all powered by intelligent agents.
                    </motion.p>

                    {/* CTA Buttons */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.3 }}
                        className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4"
                    >
                        <Link href="/dashboard">
                            <Button size="lg" className="h-12 px-8 text-base bg-black hover:bg-slate-800 text-white shadow-lg">
                                Start Free Trial
                                <ArrowRight className="ml-2 h-4 w-4" />
                            </Button>
                        </Link>
                        <Button variant="outline" size="lg" className="h-12 px-8 text-base border-slate-300 hover:bg-slate-50">
                            <Play className="mr-2 h-4 w-4" />
                            Watch Demo
                        </Button>
                    </motion.div>

                    {/* Social Proof */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.4 }}
                        className="mt-12 flex items-center justify-center gap-8 text-sm text-slate-500"
                    >
                        <div className="flex items-center gap-2">
                            <div className="flex -space-x-2">
                                {[1, 2, 3, 4].map((i) => (
                                    <div
                                        key={i}
                                        className="w-8 h-8 rounded-full bg-slate-200 border-2 border-white"
                                    />
                                ))}
                            </div>
                            <span>500+ clubs using Nexus</span>
                        </div>
                        <div className="hidden sm:flex items-center gap-1">
                            {[1, 2, 3, 4, 5].map((i) => (
                                <svg key={i} className="w-4 h-4 text-slate-900 fill-current" viewBox="0 0 20 20">
                                    <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                                </svg>
                            ))}
                            <span className="ml-1">4.9/5 rating</span>
                        </div>
                    </motion.div>

                    {/* Dashboard Preview */}
                    <motion.div
                        initial={{ opacity: 0, y: 40, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        transition={{ duration: 0.7, delay: 0.5 }}
                        className="mt-16 relative"
                    >
                        <div className="absolute inset-0 bg-gradient-to-t from-white via-transparent to-transparent z-10 pointer-events-none" />
                        <div className="rounded-xl border border-slate-200 shadow-2xl shadow-slate-200/50 overflow-hidden bg-white">
                            <div className="h-8 bg-slate-100 border-b border-slate-200 flex items-center px-4 gap-2">
                                <div className="w-3 h-3 rounded-full bg-slate-300" />
                                <div className="w-3 h-3 rounded-full bg-slate-300" />
                                <div className="w-3 h-3 rounded-full bg-slate-300" />
                            </div>
                            <div className="aspect-[16/9] bg-slate-50 flex items-center justify-center">
                                <div className="grid grid-cols-3 gap-4 p-8 w-full max-w-4xl">
                                    {/* Mock Dashboard Cards */}
                                    <div className="col-span-1 space-y-4">
                                        <div className="h-24 rounded-lg bg-white border border-slate-200 shadow-sm p-4">
                                            <div className="h-3 w-20 bg-slate-200 rounded mb-2" />
                                            <div className="h-6 w-16 bg-slate-100 rounded" />
                                        </div>
                                        <div className="h-24 rounded-lg bg-white border border-slate-200 shadow-sm p-4">
                                            <div className="h-3 w-24 bg-slate-200 rounded mb-2" />
                                            <div className="h-6 w-12 bg-slate-100 rounded" />
                                        </div>
                                    </div>
                                    <div className="col-span-2 h-52 rounded-lg bg-white border border-slate-200 shadow-sm p-4">
                                        <div className="h-3 w-32 bg-slate-200 rounded mb-4" />
                                        <div className="space-y-2">
                                            {[1, 2, 3].map((i) => (
                                                <div key={i} className="flex items-center gap-3">
                                                    <div className="w-8 h-8 rounded-full bg-slate-100" />
                                                    <div className="flex-1 h-3 bg-slate-100 rounded" />
                                                    <div className="w-16 h-6 bg-slate-100 rounded" />
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </div>
            </div>
        </section>
    );
}
