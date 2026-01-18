"use client";

import { motion } from "framer-motion";

export function DemoVideo() {
    return (
        <section id="demo-video" className="py-24 scroll-mt-28">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                {/* Section Header */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5 }}
                    className="text-center mb-12"
                >
                    <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                        See Nexus in Action
                    </h2>
                    <p className="text-lg text-slate-400 max-w-2xl mx-auto">
                        Watch how Nexus transforms the way student clubs operate
                    </p>
                </motion.div>

                {/* Video Container */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5, delay: 0.2 }}
                    className="max-w-4xl mx-auto"
                >
                    <div className="relative rounded-2xl overflow-hidden bg-slate-900/50 border border-slate-700">
                        <video
                            src="/photos/demo.mp4"
                            controls
                            className="w-full h-auto"
                        />
                    </div>
                </motion.div>
            </div>
        </section>
    );
}