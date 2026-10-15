// POST /api/explain  { statement, pid, turnstileToken? } -> { text } | { error }
// Order: Turnstile -> rate limit -> validate -> passage lookup -> one model call. What the person typed is
// never logged or stored (CLAUDE.md section 5, rule 5): logs carry counts and error kinds only.

import Anthropic from "@anthropic-ai/sdk";
import { explain, MAX_STATEMENT_CHARS } from "@/lib/explain";
import { EXPLAIN_LIMIT, MemoryRateLimiter, verifyTurnstile, visitorKey } from "@/lib/guards";
import { getPassage } from "@/lib/passages";

export const runtime = "nodejs";

const limiter = new MemoryRateLimiter(EXPLAIN_LIMIT.max, EXPLAIN_LIMIT.windowMs);

function fail(status: number, error: string, headers?: Record<string, string>) {
  return Response.json({ error }, { status, headers });
}

export async function POST(req: Request) {
  let body: { statement?: unknown; pid?: unknown; turnstileToken?: unknown };
  try {
    body = await req.json();
  } catch {
    return fail(400, "bad_request");
  }
  const statement = typeof body.statement === "string" ? body.statement.trim() : "";
  const pid = typeof body.pid === "string" ? body.pid : "";
  const token = typeof body.turnstileToken === "string" ? body.turnstileToken : undefined;

  if (!(await verifyTurnstile(token, req.headers.get("x-forwarded-for") ?? undefined))) {
    return fail(403, "bot_check_failed");
  }
  const { allowed, retryAfterSec } = await limiter.take(visitorKey(req.headers));
  if (!allowed) return fail(429, "rate_limited", { "Retry-After": String(retryAfterSec) });

  if (!statement || statement.length > MAX_STATEMENT_CHARS || !pid) return fail(400, "bad_request");
  // Crisis statements never reach a passage, so they never reach Explain; the Day 22 crisis check will
  // also run here, since this endpoint can be called directly.

  try {
    const passage = await getPassage(pid);
    if (!passage) return fail(404, "unknown_passage");
    const result = await explain(statement, passage);
    if (!result.ok) {
      console.warn(`explain: no note (${result.reason})`);
      return fail(502, "no_explanation");
    }
    console.info(`explain: ok model=${result.model} in=${result.usage.input} out=${result.usage.output}`);
    return Response.json({ text: result.text, label: "AI-generated explanation" });
  } catch (err) {
    if (err instanceof Anthropic.RateLimitError) return fail(503, "busy");
    if (err instanceof Anthropic.APIError) {
      console.error(`explain: model API error ${err.status}`);
      return fail(502, "model_error");
    }
    console.error(`explain: ${err instanceof Error ? err.name : "unknown"} error`);
    return fail(500, "server_error");
  }
}
