// POST /api/search  { statement, turnstileToken? }
//   -> { crisis: "crisis" }                                   helpline screen only, no passages
//   -> { crisis: "borderline", passages: [...] }              helpline screen first, "Continue to passages"
//   -> { crisis: "none", passages: [...] }                    up to 10 passages, best first
// Order: Turnstile -> rate limit -> validate -> crisis check and query rewrite side by side -> embed ->
// rank -> passage text. What the person typed is never logged or stored (CLAUDE.md section 5, rule 5);
// logs carry labels, counts, timings and error kinds only.

import { CRISIS_MODEL, checkCrisis, matchesCrisisPattern } from "@/lib/crisis";
import { MAX_STATEMENT_CHARS } from "@/lib/explain";
import { checkLimits, fail, limited, serverTiming, verifyTurnstile, visitorKey } from "@/lib/guards";
import { getPassages, publicView } from "@/lib/passages";

import { REWRITE_MODEL } from "@/lib/rewrite";
import { EMBED_MODEL_ID, embedQueryWithUsage, queryText, rank, safeRewrite } from "@/lib/search";
import { recordSpend } from "@/lib/spend";

export const runtime = "nodejs";
export const maxDuration = 30; // model calls time out at 10 s with one retry, run side by side; Hobby allows 300 s

export async function POST(req: Request) {
  const t0 = performance.now();
  const marks: Record<string, number> = {};
  const lap = (name: string, since: number) => (marks[name] = performance.now() - since);

  let body: { statement?: unknown; turnstileToken?: unknown };
  try {
    body = await req.json();
  } catch {
    return fail(400, "bad_request");
  }
  const statement = typeof body.statement === "string" ? body.statement.trim() : "";
  const token = typeof body.turnstileToken === "string" ? body.turnstileToken : undefined;

  if (!(await verifyTurnstile(token, req.headers.get("x-forwarded-for") ?? undefined))) {
    return fail(403, "bot_check_failed");
  }
  if (!statement || statement.length > MAX_STATEMENT_CHARS) return fail(400, "bad_request");

  try {
    const lim = await checkLimits("search", visitorKey(req.headers));
    if (!lim.allowed) return limited(lim);

    // An explicit phrase answers at once, with no model call and no rewrite to wait for.
    if (matchesCrisisPattern(statement)) {
      console.info("search: crisis via=pattern");
      return Response.json({ crisis: "crisis" }, { headers: { "Cache-Control": "no-store", "Server-Timing": serverTiming({ total: performance.now() - t0 }) } });
    }

    // The crisis check gates everything; the rewrite runs alongside it so a safe statement waits for
    // one model call, not two. A crisis statement's rewrite is simply discarded.
    let t = performance.now();
    const [crisis, rewrite] = await Promise.all([checkCrisis(statement), safeRewrite(statement)]);
    lap("models", t);
    recordSpend("search", CRISIS_MODEL, crisis.usage);
    recordSpend("search", REWRITE_MODEL, rewrite?.usage);
    if (crisis.label === "crisis") {
      console.info(`search: crisis via=${crisis.via}`);
      return Response.json({ crisis: "crisis" }, { headers: { "Cache-Control": "no-store", "Server-Timing": serverTiming({ ...marks, total: performance.now() - t0 }) } });
    }

    t = performance.now();
    const { vector, tokens } = await embedQueryWithUsage(queryText(statement, rewrite?.text ?? null));
    recordSpend("search", EMBED_MODEL_ID, { input: tokens, output: 0 });
    lap("embed", t);
    t = performance.now();
    const ranked = await rank(vector);
    const passages = await getPassages(ranked.map((r) => r.pid));
    lap("db", t);
    marks.total = performance.now() - t0;

    console.info(`search: ok crisis=${crisis.label} via=${crisis.via} rewrite=${rewrite ? "yes" : "no"} n=${passages.length} ms=${Math.round(marks.total)}`);
    return Response.json(
      { crisis: crisis.label, passages: passages.map(publicView) },
      { headers: { "Cache-Control": "no-store", "Server-Timing": serverTiming(marks) } },
    );
  } catch (err) {
    console.error(`search: ${err instanceof Error ? err.name : "unknown"} error`); // name only: a message could echo input
    return fail(500, "server_error");
  }
}
