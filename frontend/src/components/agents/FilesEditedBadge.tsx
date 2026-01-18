"use client";

import { motion } from "framer-motion";
import { FileCode, FileText, Settings, ListTodo, FileSearch } from "lucide-react";
import { cn } from "@/lib/utils";
import type { EditedFile, FileIconType } from "./types";

interface FilesEditedBadgeProps {
    files: EditedFile[];
    maxDisplay?: number;
}

// Icon mapping for file types
const FILE_ICONS: Record<FileIconType, React.ReactNode> = {
    code: <FileCode className="w-3.5 h-3.5" />,
    document: <FileText className="w-3.5 h-3.5" />,
    config: <Settings className="w-3.5 h-3.5" />,
    walkthrough: <FileSearch className="w-3.5 h-3.5" />,
    task: <ListTodo className="w-3.5 h-3.5" />,
};

// Colors for different file types
const FILE_COLORS: Record<FileIconType, string> = {
    code: "text-teal-500",
    document: "text-slate-500",
    config: "text-amber-500",
    walkthrough: "text-purple-500",
    task: "text-blue-500",
};

export function FilesEditedBadge({ files, maxDisplay = 5 }: FilesEditedBadgeProps) {
    if (files.length === 0) return null;

    const displayedFiles = files.slice(0, maxDisplay);
    const overflowCount = Math.max(0, files.length - maxDisplay);

    return (
        <div className="space-y-2">
            <div className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                Files Edited
            </div>
            <div className="flex flex-wrap gap-2">
                {displayedFiles.map((file, index) => (
                    <motion.a
                        key={`${file.path}-${index}`}
                        href={`file://${file.path}`}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: index * 0.05 }}
                        className={cn(
                            "inline-flex items-center gap-1.5 px-2 py-1",
                            "rounded-md bg-slate-50 border border-slate-200",
                            "text-xs font-medium text-slate-700",
                            "hover:bg-slate-100 hover:border-slate-300",
                            "transition-all duration-150",
                            "cursor-pointer group"
                        )}
                        title={file.path}
                    >
                        <span className={cn(
                            FILE_COLORS[file.icon],
                            "transition-colors group-hover:text-current"
                        )}>
                            {FILE_ICONS[file.icon]}
                        </span>
                        <span className="truncate max-w-[120px]">
                            {file.filename}
                        </span>
                    </motion.a>
                ))}

                {overflowCount > 0 && (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: displayedFiles.length * 0.05 }}
                        className={cn(
                            "inline-flex items-center px-2 py-1",
                            "rounded-md bg-slate-100 border border-slate-200",
                            "text-xs font-medium text-slate-500"
                        )}
                    >
                        +{overflowCount} more
                    </motion.div>
                )}
            </div>
        </div>
    );
}
