import type React from "react";
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
    title: "Nexus - AI Event Production Platform",
    description: "AI-native event production platform with intelligent agents",
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>): React.ReactElement {
    return (
        <html lang="en">
            <body className="bg-background text-primary">
                {children}
            </body>
        </html>
    );
}
