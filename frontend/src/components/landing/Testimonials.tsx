"use client";

import { motion } from "framer-motion";
import { Quote } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

const TESTIMONIALS = [
    {
        quote: "Nexus completely transformed how we run Blueprint. What used to take our team weeks now happens in days. The AI agents handle the grunt work so we can focus on making the event amazing.",
        name: "Sarah Chen",
        role: "President, Blueprint",
        org: "MIT",
        initials: "SC",
    },
    {
        quote: "We raised 40% more in sponsorships this year thanks to Nexus. The Partnerships Agent drafts better outreach emails than I ever could, and the follow-up tracking is incredibly helpful.",
        name: "Marcus Johnson",
        role: "VP Partnerships",
        org: "HackGT",
        initials: "MJ",
    },
    {
        quote: "As a small club, we don't have dedicated marketing people. Nexus's Marketing Agent creates our entire social media calendar and even suggests content ideas. It's like having a free marketing team.",
        name: "Emily Rodriguez",
        role: "Club President",
        org: "Stanford CS Club",
        initials: "ER",
    },
];

export function Testimonials() {
    return (
        <section className="py-24 scroll-mt-16" id="testimonials">
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
                        Loved by Student Leaders
                    </h2>
                    <p className="text-lg text-slate-400 max-w-2xl mx-auto">
                        See what organizers are saying about Nexus
                    </p>
                </motion.div>

                {/* Testimonials Grid */}
                <div className="grid md:grid-cols-3 gap-8">
                    {TESTIMONIALS.map((testimonial, index) => (
                        <motion.div
                            key={testimonial.name}
                            initial={{ opacity: 0, y: 30 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                        >
                            <Card className="h-full border-slate-700 bg-slate-900/50 hover:shadow-xl transition-shadow duration-300">
                                <CardContent className="p-6">
                                    <Quote className="w-10 h-10 text-slate-700 mb-4" />
                                    <p className="text-slate-300 mb-6 leading-relaxed">
                                        &ldquo;{testimonial.quote}&rdquo;
                                    </p>
                                    <div className="flex items-center gap-3">
                                        <Avatar className="h-12 w-12 border-2 border-slate-700">
                                            <AvatarFallback className="bg-white text-black font-medium">
                                                {testimonial.initials}
                                            </AvatarFallback>
                                        </Avatar>
                                        <div>
                                            <p className="font-semibold text-white">{testimonial.name}</p>
                                            <p className="text-sm text-slate-400">
                                                {testimonial.role}, {testimonial.org}
                                            </p>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
