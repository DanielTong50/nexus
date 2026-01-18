"use client";

import { useState, createContext, useContext } from "react";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from "@/components/ui/resizable";
import { Navbar } from "./Navbar";
import { ChatPanel } from "./ChatPanel";

// Context for managing chat panel state across components
interface AppShellContextType {
  isChatOpen: boolean;
  toggleChat: () => void;
  openChat: () => void;
  closeChat: () => void;
}

const AppShellContext = createContext<AppShellContextType | null>(null);

export function useAppShell() {
  const context = useContext(AppShellContext);
  if (!context) {
    throw new Error("useAppShell must be used within AppShell");
  }
  return context;
}

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const pathname = usePathname();

  const toggleChat = () => setIsChatOpen((prev) => !prev);
  const openChat = () => setIsChatOpen(true);
  const closeChat = () => setIsChatOpen(false);

  // Get current page title from pathname
  const getPageTitle = () => {
    const path = pathname.split("/")[1] || "events";
    return path.charAt(0).toUpperCase() + path.slice(1);
  };

  return (
    <AppShellContext.Provider
      value={{ isChatOpen, toggleChat, openChat, closeChat }}
    >
      <div className="h-screen w-screen overflow-hidden bg-slate-50">
        <ResizablePanelGroup orientation="horizontal" className="h-full">
          {/* Left Navigation Panel */}
          <ResizablePanel
            defaultSize={isChatOpen ? 5 : 15}
            minSize={5}
            maxSize={20}
            className="border-r border-slate-200"
          >
            <Navbar isCollapsed={isChatOpen} />
          </ResizablePanel>

          <ResizableHandle className="w-px bg-slate-200 hover:bg-slate-300 transition-colors" />

          {/* Chat Panel - Only visible when open */}
          <AnimatePresence>
            {isChatOpen && (
              <>
                <ResizablePanel
                  defaultSize={25}
                  minSize={20}
                  maxSize={40}
                  className="border-r border-slate-200"
                >
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                    className="h-full"
                  >
                    <ChatPanel onClose={closeChat} />
                  </motion.div>
                </ResizablePanel>
                <ResizableHandle className="w-px bg-slate-200 hover:bg-slate-300 transition-colors" />
              </>
            )}
          </AnimatePresence>

          {/* Main Content Panel */}
          <ResizablePanel defaultSize={isChatOpen ? 70 : 85} minSize={50}>
            <div className="h-full overflow-auto bg-white">
              {/* Page Header */}
              <motion.header
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="sticky top-0 z-10 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/80 border-b border-slate-200"
              >
                <div className="flex items-center justify-between px-6 h-16">
                  <h1 className="text-xl font-semibold text-slate-900">{getPageTitle()}</h1>
                </div>
              </motion.header>

              {/* Page Content */}
              <motion.main
                key={pathname}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.1 }}
              >
                {children}
              </motion.main>
            </div>
          </ResizablePanel>
        </ResizablePanelGroup>
      </div>
    </AppShellContext.Provider>
  );
}
