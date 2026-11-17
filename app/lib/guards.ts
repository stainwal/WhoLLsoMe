// Abuse and spend guards for the server routes (Plan section 6: Turnstile, per-visitor rate limit, spend caps).
// Counts live in Supabase (rate_limits, backend/app.sql), so every Vercel instance shares them.
// The final backstop is the Anthropic account itself: $5 prepaid, auto-reload off (Decisions, 16 Nov).

import { createHash } from "node:crypto";
import { db } from "./db";

// ---- limits ---------------------------------------------------------------------------------------------

const HOUR = 3600;
const DAY = 86400;

// Per visitor (hashed IP) per window. Search makes two Haiku calls and one embedding; Explain one Sonnet
// and one Haiku call; Surprise and access make no model call.
export const VISITOR_LIMITS = {
  search: { max: 30, windowSec: HOUR },
  explain: { max: 20, windowSec: HOUR },
  surprise: { max: 120, windowSec: HOUR },
  access: { max: 10, windowSec: HOUR }, // access-code attempts: slows guessing
  report: { max: 10, windowSec: HOUR }, // "Report this response"
} as const;

// Site-wide per day, whoever is calling: a ceiling on daily model spend even if many visitors (or one
// visitor behind many IPs) hit the routes. At Day 21 prices: 500 Explains about $1.60, 2,000 searches
// about $0.40. Raise after launch if real use needs it.
export const GLOBAL_LIMITS = {
  search: { max: 2000, windowSec: DAY },
  explain: { max: 500, windowSec: DAY },
  report: { max: 500, windowSec: DAY }, // keeps the reports table small even under abuse
} as const;

export type Route = keyof typeof VISITOR_LIMITS;

export type LimitResult = { allowed: boolean; retryAfterSec: number; scope?: "visitor" | "site" };

async function take(key: string, max: number, windowSec: number): Promise<{ allowed: boolean; retryAfterSec: number }> {
  const [row] = await db()<{ allowed: boolean; retry_after: number }[]>`
    select allowed, retry_after from take_rate(${key}, ${max}, ${windowSec})`;
  return { allowed: row.allowed, retryAfterSec: row.retry_after };
}

/** Counts one use of `route` for this visitor, then for the whole site; refuses if either is over. */
export async function checkLimits(route: Route, visitor: string): Promise<LimitResult> {
  const v = VISITOR_LIMITS[route];
  const mine = await take(`${route}:${visitor}`, v.max, v.windowSec);
  if (!mine.allowed) return { ...mine, scope: "visitor" };
  const g = (GLOBAL_LIMITS as Record<string, { max: number; windowSec: number }>)[route];
  if (g) {
    const site = await take(`global:${route}`, g.max, g.windowSec);
    if (!site.allowed) return { ...site, scope: "site" };
  }
  return { allowed: true, retryAfterSec: 0 };
}

/** A visitor key that never stores the raw IP: a salted hash, truncated. */
export function visitorKey(headers: Headers): string {
  const ip = headers.get("x-forwarded-for")?.split(",")[0]?.trim() || headers.get("x-real-ip") || "unknown";
  const salt = process.env.VISITOR_SALT;
  if (!salt && process.env.NODE_ENV === "production") throw new Error("VISITOR_SALT is not set");
  return createHash("sha256").update(`${salt ?? "whollsome-dev"}:${ip}`).digest("hex").slice(0, 32);
}

// ---- Cloudflare Turnstile hook ----------------------------------------------------------------------------

/**
 * Verifies a Turnstile token with Cloudflare. Off until TURNSTILE_SECRET_KEY is set (Plan Day 26); then a
 * missing or failed token is refused.
 */
export async function verifyTurnstile(token: string | undefined, ip?: string): Promise<boolean> {
  const secret = process.env.TURNSTILE_SECRET_KEY;
  if (!secret) return true;
  if (!token) return false;
  const body = new URLSearchParams({ secret, response: token });
  if (ip) body.set("remoteip", ip);
  const res = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
    method: "POST",
    body,
    signal: AbortSignal.timeout(5000),
  });
  if (!res.ok) return false;
  const data = (await res.json()) as { success?: boolean };
  return data.success === true;
}

// ---- shared response helpers ------------------------------------------------------------------------------

export function fail(status: number, error: string, headers?: Record<string, string>) {
  return Response.json({ error }, { status, headers: { "Cache-Control": "no-store", ...headers } });
}

export function limited(r: LimitResult) {
  return fail(429, r.scope === "site" ? "busy_today" : "rate_limited", { "Retry-After": String(r.retryAfterSec) });
}

/** Server-Timing header: how long each step took, in ms, so latency can be read from the browser. */
export function serverTiming(marks: Record<string, number>): string {
  return Object.entries(marks).map(([k, ms]) => `${k};dur=${Math.round(ms)}`).join(", ");
}
