import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-black">
            <SignIn
                appearance={{
                    elements: {
                        rootBox: "mx-auto",
                        card: "bg-slate-900 border border-slate-800",
                        headerTitle: "text-white",
                        headerSubtitle: "text-slate-400",
                        socialButtonsBlockButton: "bg-slate-800 border-slate-700 text-white hover:bg-slate-700",
                        formFieldLabel: "text-slate-300",
                        formFieldInput: "bg-slate-800 border-slate-700 text-white",
                        footerActionLink: "text-blue-400 hover:text-blue-300",
                    }
                }}
            />
        </div>
    );
}
