"use client";

import { motion } from "framer-motion";
import { useEffect, useRef } from "react";

export function DemoVideo() {
    const videoRef = useRef<HTMLVideoElement>(null);
    const sectionRef = useRef<HTMLElement>(null);

    useEffect(() => {
        const video = videoRef.current;
        const section = sectionRef.current;

        if (!video || !section) return;

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        // Play video when section comes into view
                        video.play().catch(() => {
                            // Autoplay may be blocked by browser, ignore error
                        });
                    } else {
                        // Pause video when section leaves view
                        video.pause();
                    }
                });
            },
            {
                threshold: 0.3, // Trigger when 30% of section is visible
            }
        );

        observer.observe(section);

        return () => {
            observer.disconnect();
        };
    }, []);

    return (
        <section id="demo-video" className="py-24 scroll-mt-28" ref={sectionRef}>
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
                            ref={videoRef}
                            src="/photos/demo.mp4"
                            muted
                            loop
                            playsInline
                            className="w-full h-auto"
                        />
                    </div>
                </motion.div>
            </div>
        </section>
    );
}