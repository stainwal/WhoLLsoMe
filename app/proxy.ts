// Runs before every request (Next.js 16 "proxy", formerly middleware). Applies the pre-launch gate in
// lib/gate.ts: pages show the holding page, API routes answer 401, until the access cookie is present.

import { NextResponse, type NextRequest } from "next/server";
import { ACCESS_COOKIE, hasAccess } from "@/lib/gate";

// Reachable without the access cookie: the holding page itself and the route that checks the code.
const OPEN = ["/coming-soon", "/api/access"];

export async function proxy(req: NextRequest) {
  const { pathname } = req.nextUrl;
  if (OPEN.includes(pathname) || (await hasAccess(req.cookies.get(ACCESS_COOKIE)?.value))) {
    return NextResponse.next();
  }
  if (pathname.startsWith("/api/")) {
    return NextResponse.json({ error: "gated" }, { status: 401, headers: { "Cache-Control": "no-store" } });
  }
  // Same URL, holding page content; kept out of search engines until launch.
  const res = NextResponse.rewrite(new URL("/coming-soon", req.url));
  res.headers.set("X-Robots-Tag", "noindex, nofollow");
  res.headers.set("Cache-Control", "no-store");
  return res;
}

export const config = {
  // Everything except Next's own static assets and the favicon.
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
