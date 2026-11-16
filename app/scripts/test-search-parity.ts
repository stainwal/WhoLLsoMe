// Runtime ranking == eval ranking (Day 22). For agent golden statements, feed lib/search.ts the same Haiku
// rewrite the eval used (evals/rewrites/haiku-v1.json) and compare its top 10 with the scored Setup B run
// (evals/runs/B__haiku.json): same 10 passages, same first passage; order may differ among near-ties. Costs a few Voyage query embeddings, no model calls.
//   cd app && npx tsx scripts/test-search-parity.ts [N]
import fs from "node:fs";
import path from "node:path";
import { ROOT } from "./ledger"; // also loads the repository's .env
import { db } from "../lib/db";
import { embedQuery, queryText, rank } from "../lib/search";

const n = Number(process.argv[2] ?? 8);
const run = JSON.parse(fs.readFileSync(path.join(ROOT, "evals/runs/B__haiku.json"), "utf8"));
const rw = new Map<string, string>(
  JSON.parse(fs.readFileSync(path.join(ROOT, "evals/rewrites/haiku-v1.json"), "utf8")).rewrites.map(
    (r: { id: string; query: string }) => [r.id, r.query],
  ),
);
const golden = fs.readFileSync(path.join(ROOT, "evals/agent-set.jsonl"), "utf8").trim().split("\n")
  .map((l) => JSON.parse(l)).filter((s) => s.part === "golden" && rw.has(s.id)).slice(0, n);

let same = 0, sameSet = 0;
for (const s of golden) {
  const ranked = await rank(await embedQuery(queryText(s.text, rw.get(s.id)!)));
  const got = ranked.map((r) => r.pid);
  const wantRows = (run.ranked[s.id] as [string, number][]).slice(0, 10);
  const want = wantRows.map(([p]) => p);
  const evalScore = new Map(wantRows);
  // Largest score difference for the same passage, runtime vs eval (eval scores are rounded to 4 places).
  const drift = Math.max(...ranked.map((r) => Math.abs(r.score - (evalScore.get(r.pid) ?? r.score))));
  const ok = got.join() === want.join();
  const overlap = got.filter((p) => want.includes(p)).length;
  same += ok ? 1 : 0;
  sameSet += overlap === 10 && got[0] === want[0] ? 1 : 0;
  console.log(`${ok ? "SAME" : "DIFF"}  ${s.id}  top-1 ${got[0] === want[0] ? "same" : "differs"}, ${overlap} of 10 shared, max score drift ${drift.toFixed(4)}`);
}
console.log(`${same} of ${golden.length} identical in order; ${sameSet} of ${golden.length} same 10 passages and same first passage`);
// Order can differ among near-ties: a fresh query embedding differs from the eval's cached one in the
// last decimal places. The test passes when the set and the first passage match.
await db().end();
process.exit(sameSet === golden.length ? 0 : 1);
