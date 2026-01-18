"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { X, Send, Bot, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";

interface ChatPanelProps {
  onClose?: () => void;
}

export function ChatPanel({ onClose }: ChatPanelProps) {
  const [message, setMessage] = useState("");

  const handleSend = () => {
    if (!message.trim()) return;
    // Will be connected to backend in Part 8
    console.log("Sending message:", message);
    setMessage("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex h-full flex-col bg-white">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex items-center justify-between border-b border-slate-200 px-4 h-16"
      >
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-slate-900 flex items-center justify-center">
            <Bot className="h-5 w-5 text-white" />
          </div>
          <div>
            <h2 className="font-semibold text-slate-900">Nexus AI</h2>
            <p className="text-xs text-slate-500">Your event assistant</p>
          </div>
        </div>
        {onClose && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="text-slate-500 hover:text-slate-900"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </motion.div>

      {/* Agent Feed Area */}
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {/* Welcome message */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="flex gap-3"
          >
            <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 text-slate-600" />
            </div>
            <div className="flex-1">
              <div className="rounded-2xl rounded-tl-none bg-slate-100 p-4">
                <p className="text-sm text-slate-700 leading-relaxed">
                  Hi! I&apos;m your AI assistant for event management. I can help coordinate across
                  all your teams: Partnerships, Marketing, Finance, Events, and
                  Developers.
                </p>
              </div>
              <p className="text-xs text-slate-400 mt-1 ml-2">Just now</p>
            </div>
          </motion.div>

          {/* Example capabilities */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-slate-50 rounded-xl p-4 border border-slate-100"
          >
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="w-4 h-4 text-slate-500" />
              <p className="text-xs font-medium text-slate-600">Try asking me:</p>
            </div>
            <div className="space-y-2">
              {[
                "Draft a sponsorship email to Acme Corp",
                "Create a social media post for Blueprint",
                "What's our current budget status?",
                "Show me open GitHub issues",
              ].map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => setMessage(suggestion)}
                  className="block w-full text-left text-sm text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg px-3 py-2 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </motion.div>
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="border-t border-slate-200 p-4">
        <div className="flex gap-2">
          <Textarea
            placeholder="Ask something..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            className="min-h-[60px] resize-none border-slate-200 focus:border-slate-400 focus:ring-slate-200"
            rows={2}
          />
          <Button
            size="icon"
            onClick={handleSend}
            disabled={!message.trim()}
            className="h-[60px] w-[60px] bg-slate-900 hover:bg-black text-white"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <p className="mt-2 text-xs text-slate-400">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
