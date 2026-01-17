import type { Metadata } from "next";
import "./globals.css";
import { MainLayout } from "@/components/layout/MainLayout";

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
            <body>
                <MainLayout>{children}</MainLayout>
            </body>
        </html>
    );
}
