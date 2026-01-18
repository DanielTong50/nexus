"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

interface TypewriterEffectProps {
    text: string;
    speed?: number;
    className?: string;
    onComplete?: () => void;
}

export function TypewriterEffect({
    text,
    speed = 15,
    className = "",
    onComplete,
}: TypewriterEffectProps) {
    const [displayedText, setDisplayedText] = useState("");

    useEffect(() => {
        let index = 0;
        // Reset when text changes drastically, but handling streaming appends is trickier.
        // For now, assuming text grows or is a static message.
        if (text.length < displayedText.length) {
            setDisplayedText("");
            index = 0;
        } else {
            index = displayedText.length;
        }

        const interval = setInterval(() => {
            if (index < text.length) {
                setDisplayedText((prev) => prev + text.charAt(index));
                index++;
            } else {
                clearInterval(interval);
                onComplete?.();
            }
        }, speed);

        return () => clearInterval(interval);
    }, [text, speed, onComplete, displayedText.length]);

    return (
        <span className={className}>
            {displayedText}
            <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ repeat: Infinity, duration: 0.8, ease: "linear" }}
                className="inline-block ml-0.5 w-1.5 h-4 bg-primary align-middle"
            />
        </span>
    );
}
