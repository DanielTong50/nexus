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
                    <div className="relative aspect-video rounded-2xl overflow-hidden bg-slate-900/50 border border-slate-700">
                        {/* Placeholder for video */}
                        <div className="absolute inset-0 flex items-center justify-center">
                            <div className="text-center">
                                <div className="w-20 h-20 rounded-full bg-white/10 flex items-center justify-center mx-auto mb-4 hover:bg-white/20 transition-colors cursor-pointer">
                                    <svg
                                        className="w-8 h-8 text-white ml-1"
                                        fill="currentColor"
                                        viewBox="0 0 24 24"
                                    >
                                        <path d="M8 5v14l11-7z" />
                                    </svg>
                                </div>
                                <p className="text-slate-400">Demo video coming soon</p>
                            </div>
                        </div>

                        {/* TODO: Replace with actual video embed */}
                        {/* <video 
                            src="/demo.mp4" 
                            controls 
                            className="w-full h-full object-cover"
                        /> */}

                        {/* Or YouTube embed */}
                        {/* <iframe 
                            src="https://www.youtube.com/embed/YOUR_VIDEO_ID" 
                            className="w-full h-full"
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                            allowFullScreen
                        /> */}
                    </div>
                </motion.div>
            </div>
        </section>
    );
}
