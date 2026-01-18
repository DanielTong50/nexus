"use client";

import { motion } from "framer-motion";
import {
  Bot,
  MessageSquare,
  Shield,
  Zap,
  BarChart3,
  Users,
  Clock,
  GitBranch,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const FEATURES = [
  {
    icon: Bot,
    title: "AI Agent Teams",
    description: "Five specialized AI agents handle partnerships, marketing, finance, events, and development autonomously.",
  },
  {
    icon: MessageSquare,
    title: "Natural Language Control",
    description: "Just tell Nexus what you need in plain English. No complex interfaces or steep learning curves.",
  },
  {
    icon: Shield,
    title: "Human-in-the-Loop",
    description: "AI agents ask for your approval before taking high-stakes actions like sending emails or payments.",
  },
  {
    icon: Zap,
    title: "Real-Time Streaming",
    description: "Watch your AI team work in real-time with live updates and transparent reasoning.",
  },
  {
    icon: BarChart3,
    title: "Unified Dashboard",
    description: "One place to track sponsors, social posts, budgets, issues, and event progress.",
  },
  {
    icon: Users,
    title: "Team Collaboration",
    description: "Multiple team members can work with the same AI agents simultaneously.",
  },
  {
    icon: Clock,
    title: "24/7 Operations",
    description: "Your AI team never sleeps. Draft emails, track budgets, and monitor progress around the clock.",
  },
  {
    icon: GitBranch,
    title: "GitHub Integration",
    description: "Developers can track issues, PRs, and deployments directly within Nexus.",
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export function Features() {
  return (
    <section id="features" className="py-24 bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
            Everything You Need to Run World-Class Events
          </h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Nexus combines AI agents, real-time collaboration, and powerful integrations
            to give your club superpowers.
          </p>
        </motion.div>

        {/* Features Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid md:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          {FEATURES.map((feature) => (
            <motion.div key={feature.title} variants={itemVariants}>
              <Card className="h-full border-slate-200 hover:border-slate-300 hover:shadow-lg transition-all duration-300 group bg-white">
                <CardContent className="p-6">
                  <div className="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center mb-4 group-hover:bg-slate-900 group-hover:text-white transition-colors">
                    <feature.icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-slate-600 leading-relaxed">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
