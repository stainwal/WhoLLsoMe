// POST /api/explain  { statement, pid, turnstileToken? } -> { text, label } | { crisis: "crisis" } | { error }
// Order: Turnstile -> validate -> rate limit -> passage lookup -> crisis check and Explain side by side.
// The crisis check runs here too because this endpoint can be called directly, not only after a search.
// Only "crisis" blocks the note: a "borderline" visitor has already chosen "Continue to passages".
// What the person typed is never logged or stored (CLAUDE.md section 5, rule 5).

import Anthropic from "@anthropic-ai/sdk";
import { CRISIS_MODEL, checkCrisis } from "@/lib/crisis";
import { recordSpend } from "@/lib/spend";
import { explain, MAX_STATEMENT_CHARS } from "@/lib/explain";
import { checkLimits, fail, limited, serverTiming, verifyTurnstile, visitorKey } from "@/lib/guards";
import { getPassage } from "@/lib/passages";

export const runtime = "nodejs";
export const maxDuration = 60; // Explain: 20 s timeout with one retry; Hobby allows 300 s

export async function POST(req: Request) {
  const t0 = performance.now();
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
  if (!statement || statement.length > MAX_STATEMENT_CHARS || !pid) return fail(400, "bad_request");

  try {
    const lim = await checkLimits("explain", visitorKey(req.headers));
    if (!lim.allowed) return limited(lim);

    const passage = await getPassage(pid);
    // Passages hidden from distress are never offered by search or Surprise, so never explained either.
    if (!passage || passage.hide_in_distress) return fail(404, "unknown_passage");

    const [crisis, result] = await Promise.all([checkCrisis(statement), explain(statement, passage)]);
    recordSpend("explain", CRISIS_MODEL, crisis.usage);
    recordSpend("explain", result.model, result.usage); // failed notes cost tokens too
    const timing = { "Server-Timing": serverTiming({ total: performance.now() - t0 }), "Cache-Control": "no-store" };
    if (crisis.label === "crisis") {
      console.info(`explain: crisis via=${crisis.via}`);
      return Response.json({ crisis: "crisis" }, { headers: timing });
    }
    if (!result.ok) {
      console.warn(`explain: no note (${result.reason})`);
      return fail(502, "no_explanation");
    }
    console.info(`explain: ok model=${result.model} in=${result.usage.input} out=${result.usage.output} ms=${Math.round(performance.now() - t0)}`);
    return Response.json({ text: result.text, label: "AI-generated explanation" }, { headers: timing });
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
