// Holding page until launch (Decisions, 16 Nov). While SITE_GATE is anything but "off", every page shows
// "coming soon" and every API route answers 401, unless the visitor has entered ACCESS_CODE once
// (POST /api/access), which sets an access cookie. Launch day: set SITE_GATE=off in Vercel and redeploy.
// Fails closed: if SITE_GATE or ACCESS_CODE is missing, the gate stays shut.
//
// The cookie holds a hash of the code and VISITOR_SALT, never the code itself, so a copied cookie stops
// working when either is changed (backend/app_access.py rotate ACCESS_CODE). Web Crypto only, so this file
// runs in the proxy as well as in route handlers.

export const ACCESS_COOKIE = "wl_access";
export const ACCESS_MAX_AGE = 60 * 60 * 24 * 30; // 30 days

export function gateOn(): boolean {
  return process.env.SITE_GATE !== "off";
}

export async function accessToken(): Promise<string | null> {
  const code = process.env.ACCESS_CODE;
  const salt = process.env.VISITOR_SALT;
  if (!code || !salt) return null;
  const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(`access:${salt}:${code}`));
  return Array.from(new Uint8Array(bytes), (b) => b.toString(16).padStart(2, "0")).join("");
}

/** Equal-length strings compared without an early exit, so timing reveals nothing about the match. */
export function sameString(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

export async function hasAccess(cookieValue: string | undefined): Promise<boolean> {
  if (!gateOn()) return true;
  const expected = await accessToken();
  return !!expected && !!cookieValue && sameString(cookieValue, expected);
}

/** Codes are compared case- and space-insensitively, so a code read out loud still works. */
export function normaliseCode(code: string): string {
  return code.trim().toLowerCase().replace(/\s+/g, "");
}
