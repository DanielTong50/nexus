"use client";

import { Hero } from "@/components/landing/Hero";
import { DemoVideo } from "@/components/landing/DemoVideo";
import { Features } from "@/components/landing/Features";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { MeetTheTeam } from "@/components/landing/MeetTheTeam";
import { Stats } from "@/components/landing/Stats";
import { Testimonials } from "@/components/landing/Testimonials";
import { FAQ } from "@/components/landing/FAQ";
import { CTA } from "@/components/landing/CTA";
import { Footer } from "@/components/landing/Footer";
import { LandingNavbar } from "@/components/landing/LandingNavbar";
import { GravityStarsBackground } from "@/components/animate-ui/components/backgrounds/gravity-stars";
import { Marquee } from "@/components/ui/marquee";
import { PageTransition } from "@/components/ui/PageTransition";
import Image from "next/image";

const logos = [
    { name: "Google Docs", src: "/photos/googledocs.png" },
    { name: "Slack", src: "/photos/slack.png" },
    { name: "Notion", src: "/photos/notion.png" },
    { name: "Google Sheets", src: "/photos/googlesheets.png" },
    { name: "Apollo", src: "/photos/apollo.png" },
    { name: "Google Meet", src: "/photos/googlemeet.png" },
    { name: "Microsoft Teams", src: "/photos/microsoftteams.png" },
    { name: "PowerPoint", src: "/photos/powerpoint.png" },
    { name: "Figma", src: "/photos/figma.png" },
    { name: "VS Code", src: "/photos/vscode.png" },
    { name: "Excel", src: "/photos/excel.png" },
    { name: "Discord", src: "/photos/discord.png" },
    { name: "LinkedIn", src: "/photos/linkedin.png" },
];

export default function LandingPage() {
    return (
        <PageTransition loaderDuration={800}>
            <main className="min-h-screen bg-black font-sans text-white">
                <LandingNavbar />
                <GravityStarsBackground
                    className="bg-black text-white"
                    movementSpeed={0.8}
                    starsCount={200}
                    starsSize={2}
                    starsOpacity={0.5}
                    mouseInfluence={220}
                    mouseGravity="repel"
                    gravityStrength={120}
                    glowIntensity={20}
                >
                    <Hero />

                    {/* Logo Marquee */}
                    <div className="py-16 overflow-hidden">
                        <p className="text-center text-white/70 text-lg mb-10 tracking-wide">Trusted Integrations with all your apps</p>
                        <div className="relative">
                            <div className="absolute inset-0 bg-white/5 backdrop-blur-sm border-y border-white/10" />
                            <Marquee className="[--duration:20s] py-6 relative z-10">
                                {logos.map((logo, index) => (
                                    <div key={index} className="mx-8 flex items-center justify-center w-16 h-16">
                                        <Image
                                            src={logo.src}
                                            alt={logo.name}
                                            width={64}
                                            height={64}
                                            className="opacity-80 hover:opacity-100 grayscale hover:grayscale-0 transition-all object-contain w-full h-full"
                                        />
                                    </div>
                                ))}
                            </Marquee>
                        </div>
                    </div>
                </GravityStarsBackground>

                <DemoVideo />
                <HowItWorks />
                <Stats />
                <Testimonials />
                <MeetTheTeam />
                <FAQ />
                <Footer />
            </main>
        </PageTransition>
    );
}
