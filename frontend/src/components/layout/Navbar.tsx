"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import {
  Calendar,
  Handshake,
  Megaphone,
  DollarSign,
  Code,
  MessageSquare,
  Sparkles,
  ChevronLeft,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import { useAppShell } from "./AppShell";

const NAV_ITEMS = [
  { id: "events", label: "Events", href: "/events", icon: Calendar },
  { id: "partnerships", label: "Partnerships", href: "/partnerships", icon: Handshake },
  { id: "marketing", label: "Marketing", href: "/marketing", icon: Megaphone },
  { id: "finance", label: "Finance", href: "/finance", icon: DollarSign },
  { id: "developers", label: "Developers", href: "/developers", icon: Code },
];

interface NavbarProps {
  isCollapsed?: boolean;
}

export function Navbar({ isCollapsed = false }: NavbarProps) {
  const pathname = usePathname();
  const { toggleChat, isChatOpen } = useAppShell();

  return (
    <TooltipProvider delayDuration={0}>
      <motion.nav
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
        className="flex h-full flex-col bg-white"
      >
        {/* Logo */}
        <div className={cn(
          "flex items-center border-b border-slate-200 h-16",
          isCollapsed ? "justify-center px-2" : "px-4"
        )}>
          {isCollapsed ? (
            <Tooltip>
              <TooltipTrigger asChild>
                <Link href="/" className="flex items-center justify-center">
                  <div className="w-9 h-9 rounded-lg bg-slate-900 flex items-center justify-center">
                    <Sparkles className="h-5 w-5 text-white" />
                  </div>
                </Link>
              </TooltipTrigger>
              <TooltipContent side="right">Nexus - Back to Home</TooltipContent>
            </Tooltip>
          ) : (
            <Link href="/" className="flex items-center gap-2 group">
              <div className="w-9 h-9 rounded-lg bg-slate-900 flex items-center justify-center group-hover:bg-black transition-colors">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold text-slate-900">Nexus</span>
            </Link>
          )}
        </div>

        {/* Navigation Items */}
        <div className="flex-1 py-4 px-2 space-y-1">
          {NAV_ITEMS.map((item, index) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
            const Icon = item.icon;

            if (isCollapsed) {
              return (
                <Tooltip key={item.id}>
                  <TooltipTrigger asChild>
                    <Link href={item.href}>
                      <motion.div
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.2, delay: index * 0.05 }}
                      >
                        <Button
                          variant="ghost"
                          size="icon"
                          className={cn(
                            "w-full h-10 relative",
                            isActive
                              ? "bg-slate-100 text-slate-900"
                              : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                          )}
                        >
                          {isActive && (
                            <motion.div
                              layoutId="activeNav"
                              className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-slate-900 rounded-r-full"
                              transition={{ type: "spring", bounce: 0.2, duration: 0.4 }}
                            />
                          )}
                          <Icon className="h-5 w-5" />
                        </Button>
                      </motion.div>
                    </Link>
                  </TooltipTrigger>
                  <TooltipContent side="right" className="font-medium">
                    {item.label}
                  </TooltipContent>
                </Tooltip>
              );
            }

            return (
              <Link key={item.id} href={item.href}>
                <motion.div
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.2, delay: index * 0.05 }}
                >
                  <Button
                    variant="ghost"
                    className={cn(
                      "w-full justify-start gap-3 h-10 relative",
                      isActive
                        ? "bg-slate-100 text-slate-900 font-medium"
                        : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                    )}
                  >
                    {isActive && (
                      <motion.div
                        layoutId="activeNav"
                        className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-slate-900 rounded-r-full"
                        transition={{ type: "spring", bounce: 0.2, duration: 0.4 }}
                      />
                    )}
                    <Icon className="h-5 w-5" />
                    <span>{item.label}</span>
                  </Button>
                </motion.div>
              </Link>
            );
          })}
        </div>

        {/* Bottom Actions */}
        <div className="border-t border-slate-200 p-2 space-y-1">
          {/* Back to Landing */}
          {isCollapsed ? (
            <Tooltip>
              <TooltipTrigger asChild>
                <Link href="/">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="w-full h-10 text-slate-500 hover:text-slate-900"
                  >
                    <ChevronLeft className="h-5 w-5" />
                  </Button>
                </Link>
              </TooltipTrigger>
              <TooltipContent side="right">Back to Home</TooltipContent>
            </Tooltip>
          ) : (
            <Link href="/">
              <Button
                variant="ghost"
                className="w-full justify-start gap-3 h-10 text-slate-500 hover:text-slate-900"
              >
                <ChevronLeft className="h-5 w-5" />
                <span>Back to Home</span>
              </Button>
            </Link>
          )}

          {/* Chat Button */}
          {isCollapsed ? (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant={isChatOpen ? "default" : "ghost"}
                  size="icon"
                  className={cn(
                    "w-full h-10",
                    isChatOpen
                      ? "bg-slate-900 text-white hover:bg-black"
                      : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                  )}
                  onClick={toggleChat}
                >
                  <MessageSquare className="h-5 w-5" />
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right">
                {isChatOpen ? "Close Chat" : "Open Chat"}
              </TooltipContent>
            </Tooltip>
          ) : (
            <Button
              variant={isChatOpen ? "default" : "ghost"}
              className={cn(
                "w-full justify-start gap-3 h-10",
                isChatOpen
                  ? "bg-slate-900 text-white hover:bg-black"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
              )}
              onClick={toggleChat}
            >
              <MessageSquare className="h-5 w-5" />
              <span>{isChatOpen ? "Close Chat" : "Chat with AI"}</span>
            </Button>
          )}
        </div>
      </motion.nav>
    </TooltipProvider>
  );
}
