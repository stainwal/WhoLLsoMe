// POST /api/report  { pid, reason } -> 204 | { error }
// "Report this response" (Decisions, 16 Nov): stores passage id, reason and time only, never what the
// person typed or who they are (backend/app.sql, reports). Rate-limited per visitor and site-wide.

import { db } from "@/lib/db";
import { checkLimits, fail, limited, visitorKey } from "@/lib/guards";
import { getPassage } from "@/lib/passages";
import { isReportReason } from "@/lib/report-reasons";

export const runtime = "nodejs";
export const maxDuration = 10;

export async function POST(req: Request) {
  let body: { pid?: unknown; reason?: unknown };
  try {
    body = await req.json();
  } catch {
    return fail(400, "bad_request");
  }
  const pid = typeof body.pid === "string" ? body.pid : "";
  const reason = typeof body.reason === "string" ? body.reason : "";
  if (!pid || !isReportReason(reason)) return fail(400, "bad_request");

  try {
    const lim = await checkLimits("report", visitorKey(req.headers));
    if (!lim.allowed) return limited(lim);
    if (!(await getPassage(pid))) return fail(404, "unknown_passage"); // only passages the site can show
    await db()`select add_report(${pid}, ${reason})`;
    console.info(`report: ${reason}`);
    return new Response(null, { status: 204, headers: { "Cache-Control": "no-store" } });
  } catch (err) {
    console.error(`report: ${err instanceof Error ? err.name : "unknown"} error`);
    return fail(500, "server_error");
  }
}
