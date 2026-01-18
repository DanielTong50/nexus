"use client";

import { motion } from "framer-motion";

interface LoadingScreenProps {
    isClosing?: boolean;
}

export function LoadingScreen({ isClosing = false }: LoadingScreenProps) {
    return (
        <div className="fixed inset-0 z-[100] pointer-events-none overflow-hidden">
            <motion.div
                className="absolute inset-0 bg-black"
                initial={{ x: "-100%" }}
                animate={{ x: isClosing ? "100%" : "0%" }}
                transition={{
                    duration: 0.5,
                    ease: [0.4, 0, 0.2, 1]
                }}
            />
        </div>
    );
}
