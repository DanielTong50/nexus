"use client";

import { motion } from "framer-motion";
import {
  Handshake,
  Megaphone,
  DollarSign,
  Calendar,
  Code,
  ArrowRight,
} from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const AGENTS = [
  {
    id: "partnerships",
    name: "Partnerships Agent",
    icon: Handshake,
    description: "Manages sponsor relationships, tracks outreach, and handles partnership logistics.",
    capabilities: [
      "Draft sponsorship emails",
      "Track sponsor pipeline",
      "Generate MOU documents",
      "Schedule follow-ups",
    ],
  },
  {
    id: "marketing",
    name: "Marketing Agent",
    icon: Megaphone,
    description: "Creates content, schedules posts, and manages social media campaigns.",
    capabilities: [
      "Write social posts",
      "Schedule campaigns",
      "Generate graphics prompts",
      "Track engagement",
    ],
  },
  {
    id: "finance",
    name: "Finance Agent",
    icon: DollarSign,
    description: "Tracks budgets, manages invoices, and monitors financial health.",
    capabilities: [
      "Track expenses",
      "Generate invoices",
      "Budget forecasting",
      "Payment reminders",
    ],
  },
  {
    id: "events",
    name: "Events Agent",
    icon: Calendar,
    description: "Coordinates event logistics, timelines, and attendee management.",
    capabilities: [
      "Timeline planning",
      "Venue coordination",
      "RSVP tracking",
      "Task assignments",
    ],
  },
  {
    id: "developers",
    name: "Developers Agent",
    icon: Code,
    description: "Tracks GitHub issues, manages deployments, and monitors tech progress.",
    capabilities: [
      "Issue triage",
      "PR reviews",
      "Deployment status",
      "Bug tracking",
    ],
  },
];

export function AgentTeams() {
  return (
    <section id="agents" className="py-24 bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <Badge variant="outline" className="mb-4 px-4 py-1 bg-white border-slate-300">
            Your AI Team
          </Badge>
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">
            Five Specialized Agent Teams
          </h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Each agent is an expert in their domain, working together to run your events seamlessly.
          </p>
        </motion.div>

        {/* Agent Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {AGENTS.map((agent, index) => (
            <motion.div
              key={agent.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className={index === 4 ? "lg:col-start-2" : ""}
            >
              <Card className="h-full border-slate-200 hover:border-slate-400 hover:shadow-xl transition-all duration-300 overflow-hidden group bg-white">
                <CardHeader className="bg-slate-50 border-b border-slate-100 pb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-slate-900 flex items-center justify-center group-hover:bg-black transition-colors">
                      <agent.icon className="w-5 h-5 text-white" />
                    </div>
                    <h3 className="text-lg font-semibold text-slate-900">
                      {agent.name}
                    </h3>
                  </div>
                </CardHeader>
                <CardContent className="pt-4">
                  <p className="text-slate-600 mb-4">
                    {agent.description}
                  </p>
                  <div className="space-y-2">
                    {agent.capabilities.map((capability) => (
                      <div key={capability} className="flex items-center gap-2 text-sm">
                        <ArrowRight className="w-3 h-3 text-slate-400" />
                        <span className="text-slate-700">{capability}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
