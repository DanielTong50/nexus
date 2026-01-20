import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

// Define public routes that don't require authentication
const isPublicRoute = createRouteMatcher([
    '/',                    // Landing page
    '/sign-in(.*)',         // Sign in pages
    '/sign-up(.*)',         // Sign up pages (waitlist)
    '/api/health(.*)',      // Health check endpoints
])

export default clerkMiddleware(async (auth, req) => {
    // Protect all non-public routes
    if (!isPublicRoute(req)) {
        await auth.protect()
    }
})

export const config = {
    matcher: [
        // Skip Next.js internals and static files
        '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
        // Always run for API routes
        '/(api|trpc)(.*)',
    ],
}
