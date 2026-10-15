// Abuse guards for paid endpoints (Plan section 7: Turnstile, per-visitor rate limit, hard spend caps).
// The final backstop is the monthly spend limit on the Anthropic Console account.

import { createHash } from "node:crypto";

// ---- per-visitor rate limit ----------------------------------------------------------------------------

export const EXPLAIN_LIMIT = { max: 20, windowMs: 60 * 60 * 1000 }; // 20 Explains per visitor per hour

export interface RateLimiter {
  /** Counts one use; false if the visitor is over the limit. */
  take(key: string): Promise<{ allowed: boolean; retryAfterSec: number }>;
}

// In-memory fixed window. Good for local use and a single instance only: Vercel runs several instances,
// each with its own memory, so Day 22 swaps in a shared store (a Supabase table keyed by the hashed visitor
// and the hour) behind this same interface.
export class MemoryRateLimiter implements RateLimiter {
  private hits = new Map<string, { start: number; count: number }>();
  constructor(private max: number, private windowMs: number) {}

  async take(key: string) {
    const now = Date.now();
    const cur = this.hits.get(key);
    if (!cur || now - cur.start >= this.windowMs) {
      this.hits.set(key, { start: now, count: 1 });
      return { allowed: true, retryAfterSec: 0 };
    }
    if (cur.count >= this.max) {
      return { allowed: false, retryAfterSec: Math.ceil((cur.start + this.windowMs - now) / 1000) };
    }
    cur.count += 1;
    return { allowed: true, retryAfterSec: 0 };
  }
}

/** A visitor key that never stores the raw IP: a salted hash, truncated. */
export function visitorKey(headers: Headers): string {
  const ip = headers.get("x-forwarded-for")?.split(",")[0]?.trim() || headers.get("x-real-ip") || "unknown";
  const salt = process.env.VISITOR_SALT ?? "whollsome-dev";
  return createHash("sha256").update(`${salt}:${ip}`).digest("hex").slice(0, 32);
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
  const res = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", { method: "POST", body });
  if (!res.ok) return false;
  const data = (await res.json()) as { success?: boolean };
  return data.success === true;
}
