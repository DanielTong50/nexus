"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { motion } from "framer-motion";
import { Menu, X, Sparkles, Github } from "lucide-react";
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

const SOCIAL_LINKS = [
    { icon: Github, href: "https://github.com/DanielTong50/nexus" },
    {
        imageSrc: "/photos/devpost.jpg",
        href: "https://nwhacks-2026.devpost.com/?ref_feature=challenge&ref_medium=your-open-hackathons&ref_content=Submissions+open&_gl=1*1kyvo83*_gcl_au*MTU4NzA3MDg0NC4xNzY4NDYyOTEx*_ga*MTY5Mjk4MjkxOS4xNzY4NDYyOTEx*_ga_0YHJK3Y10M*czE3Njg3NDE1NjIkbzckZzEkdDE3Njg3NDE1NjckajU1JGwwJGgw"
    },
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
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center">
                            <Sparkles className="h-5 w-5 text-black" />
                        </div>
                        <span className="text-xl font-bold text-white">Nexus</span>
                    </Link>

                    {/* Desktop Navigation */}
                    <nav className="hidden md:flex items-center gap-8">
                        {NAV_LINKS.map((link) => (
                            <a
                                key={link.href}
                                href={link.href}
                                className="text-sm font-medium text-slate-400 hover:text-white transition-colors"
                            >
                                {link.label}
                            </a>
                        ))}
                    </nav>

                    {/* CTA Buttons */}
                    <div className="hidden md:flex items-center gap-3">
                        {/* Social Links */}
                        <div className="flex items-center gap-2 mr-2">
                            {SOCIAL_LINKS.map((link, index) => (
                                <a
                                    key={index}
                                    href={link.href}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="w-9 h-9 rounded-lg bg-neutral-900 border border-neutral-800 flex items-center justify-center text-neutral-400 hover:text-white hover:bg-neutral-800 transition-all hover:scale-105"
                                >
                                    {link.icon ? (
                                        <link.icon className="h-4 w-4" />
                                    ) : (
                                        <Image
                                            src={link.imageSrc || ""}
                                            alt="Social"
                                            width={30}
                                            height={30}
                                            className="h-8 w-8 rounded-sm object-contain"
                                        />
                                    )}
                                </a>
                            ))}
                        </div>

                        <Link href="/dashboard">
                            <Button variant="ghost" size="sm">
                                Sign In
                            </Button>
                        </Link>
                        <Link href="/dashboard">
                            <Button size="sm" className="bg-white hover:bg-slate-200 text-black">
                                Get Started
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
                            <Link href="/dashboard" className="block">
                                <Button variant="outline" className="w-full">
                                    Sign In
                                </Button>
                            </Link>
                            <Link href="/dashboard" className="block">
                                <Button className="w-full bg-white hover:bg-slate-200 text-black">
                                    Get Started
                                </Button>
                            </Link>
                        </div>
                    </nav>
                </motion.div>
            </div>
        </motion.header>
    );
}
