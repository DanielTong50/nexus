import { Hero } from "@/components/landing/Hero";
import { Features } from "@/components/landing/Features";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { Stats } from "@/components/landing/Stats";
import { Testimonials } from "@/components/landing/Testimonials";
import { FAQ } from "@/components/landing/FAQ";
import { CTA } from "@/components/landing/CTA";
import { Footer } from "@/components/landing/Footer";
import { LandingNavbar } from "@/components/landing/LandingNavbar";
import { GravityStarsBackground } from "@/components/animate-ui/components/backgrounds/gravity-stars";

export default function LandingPage() {
    return (
        <GravityStarsBackground className="min-h-screen bg-black font-sans text-white">
            <LandingNavbar />
            <Hero />
            <Stats />
            <Features />
            <HowItWorks />
            <Testimonials />
            <FAQ />
            <CTA />
            <Footer />
        </GravityStarsBackground>
    );
}
