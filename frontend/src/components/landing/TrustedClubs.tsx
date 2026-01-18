"use client";

import { motion } from "framer-motion";
import { AvatarGroup, AvatarGroupTooltip } from "@/components/animate-ui/components/animate/avatar-group";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";

const CLUBS = [
    { name: "UBC BizTech", src: "/photos/biztech.png", fallback: "BT" },
    { name: "SFU Surge", src: "/photos/sfusurge.png", fallback: "SS" },
    { name: "PMC", src: "/photos/pmc.png", fallback: "PM" },
    { name: "eProjects", src: "/photos/eprojects.png", fallback: "EP" },
    { name: "Launchpad", src: "/photos/launchpad.png", fallback: "LP" },
    { name: "GDSC", src: "/photos/gdsc.png", fallback: "GD" },
    { name: "nwPlus", src: "/photos/nwplus.png", fallback: "NW" },
    { name: "UBC MA", src: "/photos/ma.png", fallback: "MA" },
];

export function TrustedClubs() {
    return (
        <section className="py-16">
            <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.5 }}
                    className="flex flex-col items-center justify-center gap-6"
                >
                    <p className="text-lg text-slate-400">
                        Made for outstanding clubs like:
                    </p>

                    <AvatarGroup className="h-16 -space-x-4">
                        {CLUBS.map((club, index) => (
                            <Avatar key={index} className="h-16 w-16 border-2 border-black bg-slate-800 rounded-xl">
                                <AvatarImage src={club.src} className="object-contain p-1 rounded-xl" />
                                <AvatarFallback className="bg-slate-700 text-white text-sm rounded-xl">
                                    {club.fallback}
                                </AvatarFallback>
                                <AvatarGroupTooltip>{club.name}</AvatarGroupTooltip>
                            </Avatar>
                        ))}
                    </AvatarGroup>
                </motion.div>
            </div>
        </section>
    );
}
