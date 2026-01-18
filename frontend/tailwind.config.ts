import type { Config } from "tailwindcss";

const config: Config = {
    darkMode: "class",
    content: [
        "./pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: "#334155",
                secondary: "#e2e8f0",
                background: "#f8fafc",
                accent: "#3b82f6",
                success: "#22c55e",
                warning: "#f59e0b",
                error: "#ef4444",
            },
        },
    },
    plugins: [],
};

export default config;
