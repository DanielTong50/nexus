"use client";

import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";

export function ThinkingBadge() {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="inline-flex items-center gap-2 px-3 py-1 bg-blue-500/10 border border-blue-500/20 text-blue-500 rounded-full text-xs font-medium"
        >
            <Sparkles className="w-3 h-3 animate-pulse" />
            <span>Thinking...</span>
            <span className="flex gap-1 ml-1">
                <motion.span
                    animate={{ opacity: [0, 1, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0 }}
                    className="w-1 h-1 bg-current rounded-full"
                />
                <motion.span
                    animate={{ opacity: [0, 1, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0.3 }}
                    className="w-1 h-1 bg-current rounded-full"
                />
                <motion.span
                    animate={{ opacity: [0, 1, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0.6 }}
                    className="w-1 h-1 bg-current rounded-full"
                />
            </span>
        </motion.div>
    );
}
