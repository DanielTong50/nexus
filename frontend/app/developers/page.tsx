import type React from "react";

export default function DevelopersPage(): React.ReactElement {
    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold text-primary">Developers</h1>
            <p className="text-slate-500 mt-1">Track issues, PRs, and deployments</p>
        </div>
    );
}
