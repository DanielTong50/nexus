"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

export function CTA() {
  return (
    <section className="py-24 bg-slate-50 relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#e5e7eb_1px,transparent_1px),linear-gradient(to_bottom,#e5e7eb_1px,transparent_1px)] bg-[size:32px_32px]" />

      {/* Gradient Orbs */}
      <div className="absolute top-0 left-1/4 w-64 h-64 bg-slate-200 rounded-full blur-3xl opacity-50" />
      <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-slate-100 rounded-full blur-3xl opacity-50" />

      <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <div className="inline-flex items-center gap-2 bg-slate-100 text-slate-700 px-4 py-2 rounded-full text-sm font-medium mb-6 border border-slate-200">
            <Sparkles className="w-4 h-4" />
            Free for student organizations
          </div>

          <h2 className="text-4xl md:text-5xl font-bold text-slate-900 mb-6">
            Ready to Transform Your Events?
          </h2>

          <p className="text-xl text-slate-600 mb-10 max-w-2xl mx-auto">
            Join hundreds of student organizations using Nexus to run better events
            with less stress. Start your free trial today.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/events">
              <Button size="lg" className="h-14 px-10 text-lg bg-black hover:bg-slate-800 text-white shadow-lg">
                Get Started Free
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Button variant="outline" size="lg" className="h-14 px-10 text-lg border-slate-300 hover:bg-white">
              Schedule a Demo
            </Button>
          </div>

          <p className="mt-6 text-sm text-slate-500">
            No credit card required. Free for qualifying student organizations.
          </p>
        </motion.div>
      </div>
    </section>
  );
}
