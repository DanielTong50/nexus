"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";
import { cn } from "@/lib/utils";

interface FlashRowProps {
    children: ReactNode;
    className?: string;
    flashColor?: string; // e.g. "bg-yellow-500/20"
    duration?: number;
}

export function FlashRow({
    children,
    className = "",
    flashColor = "bg-yellow-500/20",
    duration = 1.5,
}: FlashRowProps) {
    return (
        <motion.div
            initial={{ backgroundColor: "rgba(234, 179, 8, 0.3)" }}
            animate={{ backgroundColor: "rgba(0, 0, 0, 0)" }}
            transition={{ duration: duration, ease: "easeOut" }}
            className={cn("w-full", flashColor, className)}
        >
            {children}
        </motion.div>
    );
}
