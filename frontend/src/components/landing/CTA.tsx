"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

export function CTA() {
    return (
        <section className="py-24 relative overflow-hidden">
            {/* Background Pattern */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#334155_1px,transparent_1px),linear-gradient(to_bottom,#334155_1px,transparent_1px)] bg-[size:32px_32px] opacity-20" />

            {/* Gradient Orbs */}
            <div className="absolute top-0 left-1/4 w-64 h-64 bg-slate-700 rounded-full blur-3xl opacity-30" />
            <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-slate-800 rounded-full blur-3xl opacity-30" />

            <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5 }}
                >
                    <div className="inline-flex items-center gap-2 bg-slate-800 text-slate-300 px-4 py-2 rounded-full text-sm font-medium mb-6 border border-slate-700">
                        <Sparkles className="w-4 h-4" />
                        Free for student organizations
                    </div>

                    <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
                        Ready to Transform Your Events?
                    </h2>

                    <p className="text-xl text-slate-400 mb-10 max-w-2xl mx-auto">
                        Join hundreds of student organizations using Nexus to run better events
                        with less stress. Start your free trial today.
                    </p>

                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <Link href="/sign-up">
                            <Button size="lg" className="h-14 px-10 text-lg bg-white hover:bg-slate-200 text-black shadow-lg">
                                Join the Waitlist
                                <ArrowRight className="ml-2 h-5 w-5" />
                            </Button>
                        </Link>
                        <Button variant="outline" size="lg" className="h-14 px-10 text-lg border-slate-600 text-white hover:bg-slate-800">
                            Schedule a Demo
                        </Button>
                    </div>

                    <p className="mt-6 text-sm text-slate-400">
                        No credit card required. Free for qualifying student organizations.
                    </p>
                </motion.div>
            </div>
        </section>
    );
}
