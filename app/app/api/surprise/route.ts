// GET /api/surprise -> { passage } : one random passage of quotability 4-5, never one hidden from distress.
// No AI call (Plan section 2.1, item 4).

import { checkLimits, fail, limited, serverTiming, visitorKey } from "@/lib/guards";
import { publicView, surprisePassage } from "@/lib/passages";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 10;

export async function GET(req: Request) {
  const t0 = performance.now();
  try {
    const lim = await checkLimits("surprise", visitorKey(req.headers));
    if (!lim.allowed) return limited(lim);
    const p = await surprisePassage();
    if (!p) return fail(404, "no_passage");
    return Response.json(
      { passage: publicView(p) },
      { headers: { "Cache-Control": "no-store", "Server-Timing": serverTiming({ total: performance.now() - t0 }) } },
    );
  } catch (err) {
    console.error(`surprise: ${err instanceof Error ? err.name : "unknown"} error`);
    return fail(500, "server_error");
  }
}
