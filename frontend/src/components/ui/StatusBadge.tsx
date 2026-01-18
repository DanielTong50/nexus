"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Check, Loader2, X } from "lucide-react";

interface StatusBadgeProps {
    status: "pending" | "running" | "success" | "error";
    className?: string;
}

export function StatusBadge({ status, className = "" }: StatusBadgeProps) {
    return (
        <div className={`relative w-5 h-5 flex items-center justify-center ${className}`}>
            <AnimatePresence mode="wait">
                {status === "running" || status === "pending" ? (
                    <motion.div
                        key="loading"
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                    >
                        <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
                    </motion.div>
                ) : status === "success" ? (
                    <motion.div
                        key="success"
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                    >
                        <Check className="w-4 h-4 text-green-500" />
                    </motion.div>
                ) : (
                    <motion.div
                        key="error"
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                    >
                        <X className="w-4 h-4 text-red-500" />
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
