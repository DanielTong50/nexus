"use client";

import { motion } from "framer-motion";
import Image from "next/image";

const TEAM_MEMBERS = [
    {
        name: "Chris Lee",
        role: "Frontend Developer",
        school: "UBC",
        image: "/photos/chrislee.jpg",
    },
    {
        name: "Darius Alexander",
        role: "Frontend Developer",
        school: "UBC",
        image: "/photos/dariusalexander.jpg",
    },
    {
        name: "Daniel Tong",
        role: "Backend Developer",
        school: "UBC",
        image: "/photos/danieltong.jpeg",
    },
    {
        name: "Jimmy Sam",
        role: "Backend Developer",
        school: "UBC",
        image: "/photos/jimmysam.jpeg",
    },
];

export function MeetTheTeam() {
    return (
        <section id="meet-the-team" className="py-24 scroll-mt-28">
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
                        Meet the Team
                    </h2>
                    <p className="text-lg text-slate-400 max-w-2xl mx-auto">
                        The talented developers behind Nexus
                    </p>
                </motion.div>

                {/* Team Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
                    {TEAM_MEMBERS.map((member, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                            className="text-center group"
                        >
                            {/* Image Container */}
                            <div className="relative w-40 h-40 mx-auto mb-6 rounded-full overflow-hidden bg-slate-800 border-2 border-slate-700 group-hover:border-white/50 transition-colors">
                                {member.image.includes("placeholder") ? (
                                    /* Placeholder icon */
                                    <div className="absolute inset-0 flex items-center justify-center text-slate-500">
                                        <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
                                            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                                        </svg>
                                    </div>
                                ) : (
                                    /* Actual image */
                                    <Image
                                        src={member.image}
                                        alt={member.name}
                                        fill
                                        className="object-cover object-top"
                                    />
                                )}
                            </div>

                            {/* Info */}
                            <h3 className="text-xl font-semibold text-white mb-1">
                                {member.name}
                            </h3>
                            <p className="text-sm font-medium text-slate-300 mb-1">
                                {member.role}
                            </p>
                            <p className="text-sm text-slate-500">
                                {member.school}
                            </p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
