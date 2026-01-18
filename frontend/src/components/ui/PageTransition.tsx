"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { LoadingScreen } from "./LoadingScreen";

interface PageTransitionProps {
    children: React.ReactNode;
    showLoader?: boolean;
    loaderDuration?: number;
}

export function PageTransition({
    children,
    showLoader = true,
    loaderDuration = 1500
}: PageTransitionProps) {
    const [phase, setPhase] = useState<"closing" | "hold" | "opening" | "done">("closing");

    useEffect(() => {
        if (!showLoader) {
            setPhase("done");
            return;
        }

        // Phase 1: Panel slides in (0 -> 400ms)
        const holdTimer = setTimeout(() => {
            setPhase("hold");
        }, 400);

        // Phase 2: Hold (400ms -> loaderDuration)
        const openTimer = setTimeout(() => {
            setPhase("opening");
        }, loaderDuration);

        // Phase 3: Panel slides out (loaderDuration -> loaderDuration + 400ms)
        const doneTimer = setTimeout(() => {
            setPhase("done");
        }, loaderDuration + 400);

        return () => {
            clearTimeout(holdTimer);
            clearTimeout(openTimer);
            clearTimeout(doneTimer);
        };
    }, [showLoader, loaderDuration]);

    return (
        <>
            {phase !== "done" && (
                <LoadingScreen isClosing={phase === "opening"} />
            )}

            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: phase === "done" || phase === "opening" ? 1 : 0 }}
                transition={{ duration: 0.4 }}
            >
                {children}
            </motion.div>
        </>
    );
}
