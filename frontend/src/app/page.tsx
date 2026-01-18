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
import Image from "next/image";

const logos = [
    { name: "Google Docs", src: "/photos/googledocs.png" },
    { name: "Slack", src: "/photos/slack.png" },
    { name: "Notion", src: "/photos/notion.png" },
    { name: "Google Sheets", src: "/photos/googlesheets.png" },
];

export default function LandingPage() {
    return (
        <main className="min-h-screen bg-black font-sans text-white">
            <LandingNavbar />
            <GravityStarsBackground className="bg-black text-white">
                <Hero />

                {/* Logo Marquee */}
                <div className="py-12 overflow-hidden">
                    <p className="text-center text-slate-400 text-2xl mb-8 text-white">Trusted integrations with your favorite tools...</p>
                    <Marquee className="[--duration:6s]">
                        {logos.map((logo, index) => (
                            <div key={index} className="mx-8 flex items-center justify-center w-16 h-16">
                                <Image
                                    src={logo.src}
                                    alt={logo.name}
                                    width={64}
                                    height={64}
                                    className="opacity-70 hover:opacity-100 transition-opacity grayscale hover:grayscale-0 object-contain w-full h-full"
                                />
                            </div>
                        ))}
                    </Marquee>
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
    );
}
