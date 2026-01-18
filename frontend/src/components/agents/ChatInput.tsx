"use client";

import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { ArrowUp, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatInputProps {
    onSubmit: (message: string) => void;
    isLoading?: boolean;
    placeholder?: string;
    disabled?: boolean;
}

export function ChatInput({
    onSubmit,
    isLoading = false,
    placeholder = "Ask the agent anything...",
    disabled = false
}: ChatInputProps) {
    const [value, setValue] = useState("");
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    // Auto-resize textarea
    useEffect(() => {
        const textarea = textareaRef.current;
        if (textarea) {
            textarea.style.height = 'auto';
            textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
        }
    }, [value]);

    const handleSubmit = (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!value.trim() || isLoading || disabled) return;

        onSubmit(value.trim());
        setValue("");

        // Reset textarea height
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    const isSubmitDisabled = !value.trim() || isLoading || disabled;

    return (
        <form onSubmit={handleSubmit} className="p-4 bg-white border-t border-slate-200">
            <div className={cn(
                "relative rounded-2xl border bg-slate-50",
                "transition-all duration-200",
                "focus-within:border-slate-300 focus-within:bg-white",
                disabled ? "opacity-50" : "border-slate-200"
            )}>
                {/* Input Area */}
                <div className="flex items-end gap-3 p-3">
                    {/* Textarea */}
                    <textarea
                        ref={textareaRef}
                        value={value}
                        onChange={(e) => setValue(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder={placeholder}
                        disabled={disabled || isLoading}
                        rows={1}
                        className={cn(
                            "flex-1 resize-none outline-none",
                            "text-sm text-slate-900 placeholder:text-slate-400",
                            "bg-transparent",
                            "disabled:cursor-not-allowed"
                        )}
                        style={{ minHeight: '24px', maxHeight: '150px' }}
                    />

                    {/* Submit Button */}
                    <motion.button
                        type="submit"
                        disabled={isSubmitDisabled}
                        whileTap={{ scale: 0.95 }}
                        className={cn(
                            "flex-shrink-0 p-1.5 rounded-lg",
                            "transition-all duration-200",
                            isSubmitDisabled
                                ? "bg-slate-200 text-slate-400 cursor-not-allowed"
                                : "bg-slate-900 text-white hover:bg-slate-800"
                        )}
                    >
                        {isLoading ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                            <ArrowUp className="w-4 h-4" />
                        )}
                    </motion.button>
                </div>
            </div>
        </form>
    );
}
