"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import { Menu, X, Github } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const NAV_LINKS = [
    { label: "How it Works", href: "#how-it-works" },
    { label: "Why Nexus Wins", href: "#stats" },
    { label: "Meet the Team", href: "#meet-the-team" },
    // { label: "DevPost", href: "https://nwhacks-2026.devpost.com/?ref_feature=challenge&ref_medium=your-open-hackathons&ref_content=Submissions+open&_gl=1*1kyvo83*_gcl_au*MTU4NzA3MDg0NC4xNzY4NDYyOTEx*_ga*MTY5Mjk4MjkxOS4xNzY4NDYyOTEx*_ga_0YHJK3Y10M*czE3Njg3NDE1NjIkbzckZzEkdDE3Njg3NDE1NjckajU1JGwwJGgw" },
    // { label: "GitHub", href: "https://github.com/DanielTong50/nexus" },
    { label: "FAQ", href: "#faq" }
];

export function LandingNavbar() {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <motion.header
            initial={{ y: -100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-lg border-b border-slate-800"
        >
            <div className="w-full px-6 sm:px-12 lg:px-24">
                <div className="flex items-center justify-between h-16">
                    {/* Left side - Nexus text + Navigation */}
                    <div className="flex items-center gap-8">
                        <Link href="/" className="text-3xl font-bold text-white leading-none">
                            Nexus
                        </Link>
                        <nav className="hidden md:flex items-center gap-8">
                            {NAV_LINKS.map((link) => (
                                <a
                                    key={link.href}
                                    href={link.href}
                                    className="text-sm font-medium text-white hover:text-slate-300 transition-colors leading-none"
                                >
                                    {link.label}
                                </a>
                            ))}
                        </nav>
                    </div>

                    {/* Right side - Social box + Sign In */}
                    <div className="hidden md:flex items-center gap-3">
                        {/* Combined GitHub / DevPost box */}
                        <div className="h-10 px-4 rounded-lg bg-neutral-900 border border-neutral-800 flex items-center gap-3">
                            <span className="text-sm text-white">View Source</span>
                            <a
                                href="https://github.com/DanielTong50/nexus"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-neutral-400 hover:text-white transition-colors"
                            >
                                <Github className="h-6 w-6" />
                            </a>
                            <span className="text-neutral-600">/</span>
                            <a
                                href="https://nwhacks-2026.devpost.com/?ref_feature=challenge&ref_medium=your-open-hackathons&ref_content=Submissions+open"
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-neutral-400 hover:text-white transition-colors"
                            >
                                <Image
                                    src="/photos/devpost.jpg"
                                    alt="DevPost"
                                    width={32}
                                    height={32}
                                    className="h-9 w-9 rounded-sm object-contain"
                                />
                            </a>
                        </div>

                        <Link href="/sign-up">
                            <Button className="bg-white hover:bg-slate-200 text-black font-semibold px-6 h-10 text-sm">
                                Join Waitlist
                            </Button>
                        </Link>
                    </div>

                    {/* Mobile Menu Button */}
                    <button
                        onClick={() => setIsOpen(!isOpen)}
                        className="md:hidden p-2 rounded-lg hover:bg-slate-800 text-white"
                    >
                        {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                    </button>
                </div>

                {/* Mobile Menu */}
                <motion.div
                    initial={false}
                    animate={{ height: isOpen ? "auto" : 0, opacity: isOpen ? 1 : 0 }}
                    className={cn("md:hidden overflow-hidden", !isOpen && "pointer-events-none")}
                >
                    <nav className="py-4 space-y-2">
                        {NAV_LINKS.map((link) => (
                            <a
                                key={link.href}
                                href={link.href}
                                onClick={() => setIsOpen(false)}
                                className="block px-4 py-2 text-sm font-medium text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg"
                            >
                                {link.label}
                            </a>
                        ))}
                        <div className="pt-4 px-4 space-y-2">
                            <div className="flex items-center justify-center gap-4 py-2">
                                <a
                                    href="https://github.com/DanielTong50/nexus"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-neutral-400 hover:text-white transition-colors"
                                >
                                    <Github className="h-5 w-5" />
                                </a>
                                <span className="text-neutral-600">/</span>
                                <a
                                    href="https://nwhacks-2026.devpost.com/?ref_feature=challenge&ref_medium=your-open-hackathons&ref_content=Submissions+open"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-neutral-400 hover:text-white transition-colors"
                                >
                                    <Image
                                        src="/photos/devpost.jpg"
                                        alt="DevPost"
                                        width={20}
                                        height={20}
                                        className="h-5 w-5 rounded-sm object-contain"
                                    />
                                </a>
                            </div>
                            <Link href="/sign-up" className="block">
                                <Button className="w-full bg-white hover:bg-slate-200 text-black">
                                    Join Waitlist
                                </Button>
                            </Link>
                        </div>
                    </nav>
                </motion.div>
            </div>
        </motion.header>
    );
}
