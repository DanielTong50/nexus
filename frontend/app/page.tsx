"use client";

import Image from "next/image";
import { EVENTS, useEvent } from "@/lib/event-context";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowRight, Calendar, MapPin, Users } from "lucide-react";

export default function HomePage() {
    const { setEvent } = useEvent();

    // Mock data for extra card details to make them pop
    const getEventDetails = (id: string) => {
        switch (id) {
            case 'blueprint': return { date: 'Mar 15, 2026', location: 'UBC', attendees: '500+' };
            case 'produhacks': return { date: 'Jun 20, 2026', location: 'SFU', attendees: '300+' };
            case 'techstrat': return { date: 'Sep 10, 2026', location: 'Vancouver', attendees: '150+' };
            default: return { date: 'TBD', location: 'TBD', attendees: '0' };
        }
    };

    return (
        <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-muted/20">
            <div className="max-w-5xl w-full space-y-16">
                {/* Branding Header */}
                <div className="text-center space-y-8 flex flex-col items-center">
                    <div className="relative w-80 h-24 transform hover:scale-105 transition-transform duration-500">
                        <Image
                            src="/logo.png"
                            alt="Nexus"
                            fill
                            className="object-contain"
                            priority
                        />
                    </div>
                    <div className="space-y-4">
                        <h1 className="text-5xl font-extrabold tracking-tight">
                            <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary via-blue-600 to-primary/80 animate-gradient">
                                Event Production Platform
                            </span>
                        </h1>
                        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                            Select an active workspace to begin.
                        </p>
                    </div>
                </div>

                {/* Event Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {EVENTS.map((event) => {
                        const details = getEventDetails(event.id);
                        return (
                            <Card
                                key={event.id}
                                className="cursor-pointer hover:border-primary hover:shadow-lg transition-all duration-300 group relative overflow-hidden h-[320px] flex flex-col"
                                onClick={() => setEvent(event.id)}
                            >
                                {/* Top accent bar */}
                                <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-transparent via-primary/20 to-transparent group-hover:via-primary transition-all duration-500" />

                                <CardHeader className="space-y-4 pb-4">
                                    <div className="flex justify-between items-start">
                                        <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary group-hover:scale-110 transition-transform duration-300">
                                            <Calendar className="h-5 w-5" />
                                        </div>
                                        <div className="rounded-full px-2.5 py-0.5 text-xs font-semibold bg-secondary text-secondary-foreground group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                                            {event.id === 'blueprint' ? 'Active' : 'Planning'}
                                        </div>
                                    </div>
                                    <div className="space-y-1">
                                        <CardTitle className="text-2xl pt-2 group-hover:text-primary transition-colors">
                                            {event.name}
                                        </CardTitle>
                                        <CardDescription className="text-base line-clamp-2">
                                            {event.description}
                                        </CardDescription>
                                    </div>
                                </CardHeader>

                                <CardContent className="mt-auto space-y-4 border-t bg-muted/10 pt-4">
                                    <div className="grid grid-cols-2 gap-y-2 text-sm text-muted-foreground">
                                        <div className="flex items-center gap-2">
                                            <MapPin className="h-3.5 w-3.5" />
                                            {details.location}
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <Users className="h-3.5 w-3.5" />
                                            {details.attendees}
                                        </div>
                                    </div>

                                    <div className="flex items-center text-sm font-medium text-primary opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all duration-300 pb-1">
                                        Enter Workspace <ArrowRight className="ml-2 h-4 w-4" />
                                    </div>
                                </CardContent>
                            </Card>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
