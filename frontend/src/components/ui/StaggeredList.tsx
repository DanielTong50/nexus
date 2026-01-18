"use client";

import { motion } from "framer-motion";
import { Children, ReactNode } from "react";

interface StaggeredListProps {
    children: ReactNode;
    className?: string;
    delay?: number;
    staggerDelay?: number;
}

export function StaggeredList({
    children,
    className = "",
    delay = 0,
    staggerDelay = 0.05,
}: StaggeredListProps) {
    const containerVariants = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: staggerDelay,
                delayChildren: delay,
            },
        },
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 10 },
        show: { opacity: 1, y: 0, transition: { duration: 0.3 } },
    };

    return (
        <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="show"
            className={className}
        >
            {Children.map(children, (child) => (
                <motion.div variants={itemVariants}>{child}</motion.div>
            ))}
        </motion.div>
    );
}
