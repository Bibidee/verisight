import { NextRequest, NextResponse } from "next/server";
import { createServerClient, type CookieOptions } from "@supabase/ssr";

// Only refresh the Supabase session on routes that actually need an
// authenticated user. Skips marketing, auth pages, and all static assets so
// dev navigation isn't blocked by a Supabase round-trip per request.
const SESSION_PREFIXES = [
  "/dashboard",
  "/workspaces",
  "/audits",
  "/evidence",
  "/snapshots",
  "/verdicts",
  "/memos",
  "/trace",
  "/admin",
  "/profile",
  "/settings",
  "/onboarding",
];

export async function middleware(req: NextRequest) {
  const path = req.nextUrl.pathname;
  if (!SESSION_PREFIXES.some((p) => path === p || path.startsWith(p + "/"))) {
    return NextResponse.next();
  }

  const res = NextResponse.next();
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return req.cookies.getAll();
        },
        setAll(toSet: { name: string; value: string; options: CookieOptions }[]) {
          for (const { name, value, options } of toSet) {
            res.cookies.set(name, value, options);
          }
        },
      },
    },
  );
  await supabase.auth.getUser();
  return res;
}

export const config = {
  // Skip Next internals + common static assets at the matcher level too.
  matcher: ["/((?!_next/static|_next/image|_next/data|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico|css|js|map)$).*)"],
};
