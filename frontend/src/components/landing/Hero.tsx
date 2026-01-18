"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Play } from "lucide-react";
import { Button } from "@/components/ui/button";

export function Hero() {
    return (
        <section className="relative min-h-screen flex items-center overflow-hidden pt-16">

            <div className="relative z-10 max-w-4xl pl-4 sm:pl-8 lg:pl-16 pr-4 py-20">
                <div className="text-left">

                    {/* Headline */}
                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5, delay: 0.1 }}
                        className="text-5xl md:text-6xl lg:text-7xl font-bold text-white tracking-tight"
                    >
                        Deploy the #1
                        <span className="block mt-2">
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
                        className="mt-6 text-xl md:text-2xl text-slate-300 max-w-3xl leading-relaxed"
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
                                Start Free Trial
                                <ArrowRight className="ml-2 h-4 w-4" />
                            </Button>
                        </Link>
                        <Button variant="outline" size="lg" className="h-12 px-8 text-base border-slate-600 bg-transparent text-white hover:bg-slate-800">
                            <Play className="mr-2 h-4 w-4" />
                            Watch Demo
                        </Button>
                    </motion.div>

                    {/* Dashboard Preview */}
                    <motion.div
                        initial={{ opacity: 0, y: 40, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        transition={{ duration: 0.7, delay: 0.5 }}
                        className="mt-16 relative"
                    >
                        <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent z-10 pointer-events-none" />
                        <div className="rounded-xl border border-slate-700 shadow-2xl shadow-black/50 overflow-hidden bg-slate-900">
                            <div className="h-8 bg-slate-800 border-b border-slate-700 flex items-center px-4 gap-2">
                                <div className="w-3 h-3 rounded-full bg-slate-600" />
                                <div className="w-3 h-3 rounded-full bg-slate-600" />
                                <div className="w-3 h-3 rounded-full bg-slate-600" />
                            </div>
                            <div className="aspect-[16/9] bg-slate-900 flex items-center justify-center">
                                <div className="grid grid-cols-3 gap-4 p-8 w-full max-w-4xl">
                                    {/* Mock Dashboard Cards */}
                                    <div className="col-span-1 space-y-4">
                                        <div className="h-24 rounded-lg bg-slate-800 border border-slate-700 shadow-sm p-4">
                                            <div className="h-3 w-20 bg-slate-600 rounded mb-2" />
                                            <div className="h-6 w-16 bg-slate-700 rounded" />
                                        </div>
                                        <div className="h-24 rounded-lg bg-slate-800 border border-slate-700 shadow-sm p-4">
                                            <div className="h-3 w-24 bg-slate-600 rounded mb-2" />
                                            <div className="h-6 w-12 bg-slate-700 rounded" />
                                        </div>
                                    </div>
                                    <div className="col-span-2 h-52 rounded-lg bg-slate-800 border border-slate-700 shadow-sm p-4">
                                        <div className="h-3 w-32 bg-slate-600 rounded mb-4" />
                                        <div className="space-y-2">
                                            {[1, 2, 3].map((i) => (
                                                <div key={i} className="flex items-center gap-3">
                                                    <div className="w-8 h-8 rounded-full bg-slate-700" />
                                                    <div className="flex-1 h-3 bg-slate-700 rounded" />
                                                    <div className="w-16 h-6 bg-slate-700 rounded" />
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
