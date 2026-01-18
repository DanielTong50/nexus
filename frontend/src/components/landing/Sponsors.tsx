"use client";

import { motion } from "framer-motion";

const SPONSORS = [
  { name: "MIT", logo: "MIT" },
  { name: "Stanford", logo: "Stanford" },
  { name: "Berkeley", logo: "Berkeley" },
  { name: "Harvard", logo: "Harvard" },
  { name: "Yale", logo: "Yale" },
  { name: "Princeton", logo: "Princeton" },
];

export function Sponsors() {
  return (
    <section className="py-16 bg-white border-y border-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-center text-sm font-medium text-slate-500 mb-8"
        >
          TRUSTED BY STUDENT ORGANIZATIONS AT
        </motion.p>

        <div className="relative overflow-hidden">
          <motion.div
            initial={{ x: 0 }}
            animate={{ x: "-50%" }}
            transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
            className="flex gap-16 items-center"
          >
            {[...SPONSORS, ...SPONSORS].map((sponsor, index) => (
              <div
                key={index}
                className="flex-shrink-0 h-12 px-8 flex items-center justify-center"
              >
                <span className="text-2xl font-bold text-slate-300 hover:text-slate-400 transition-colors">
                  {sponsor.logo}
                </span>
              </div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
}
