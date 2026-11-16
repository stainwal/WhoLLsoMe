// POST /api/access  { code } -> 204 with the access cookie | 401 { error: "wrong_code" } | 429
// Lets Shailesh and testers past the holding page before launch (lib/gate.ts). Attempts are rate-limited
// per visitor, so the code can't be guessed by brute force; codes are never logged.

import { cookies } from "next/headers";
import { ACCESS_COOKIE, ACCESS_MAX_AGE, accessToken, gateOn, normaliseCode, sameString } from "@/lib/gate";
import { checkLimits, fail, limited, visitorKey } from "@/lib/guards";

export const runtime = "nodejs";
export const maxDuration = 10;

export async function POST(req: Request) {
  if (!gateOn()) return new Response(null, { status: 204 });
  let code = "";
  try {
    const body = (await req.json()) as { code?: unknown };
    code = typeof body.code === "string" ? normaliseCode(body.code).slice(0, 100) : "";
  } catch {
    return fail(400, "bad_request");
  }
  try {
    const lim = await checkLimits("access", visitorKey(req.headers));
    if (!lim.allowed) return limited(lim);
  } catch {
    return fail(500, "server_error");
  }
  const expected = process.env.ACCESS_CODE;
  const token = await accessToken();
  if (!expected || !token || !sameString(code, normaliseCode(expected))) return fail(401, "wrong_code");

  (await cookies()).set(ACCESS_COOKIE, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: ACCESS_MAX_AGE,
  });
  return new Response(null, { status: 204, headers: { "Cache-Control": "no-store" } });
}
