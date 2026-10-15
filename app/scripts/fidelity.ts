// (b)/(c) Fidelity checks: the same items through the real API, to compare with the subscription outputs.
//   npx tsx scripts/fidelity.ts explain ID ID ...   -> evals/explain/sonnet-api.json
//   npx tsx scripts/fidelity.ts rewrite ID ID ...   -> evals/rewrites/haiku-api.json
import fs from "node:fs";
import path from "node:path";
import { explain, EXPLAIN_MODEL } from "../lib/explain";
import { rewriteQuery, REWRITE_MODEL } from "../lib/rewrite";
import { guardCap, record, ROOT, spentSoFar } from "./ledger";

const [kind, ...ids] = process.argv.slice(2);
const pairs = fs.readFileSync(path.join(ROOT, "evals/explain/pairs.jsonl"), "utf8").trim().split("\n").map((l) => JSON.parse(l));
const queries = fs.readFileSync(path.join(ROOT, "evals/judge-in/q01.jsonl"), "utf8").trim().split("\n").map((l) => JSON.parse(l));

if (kind === "explain") {
  const notes: Record<string, string> = {};
  for (const id of ids) {
    guardCap();
    const p = pairs.find((x: { id: string }) => x.id === id);
    const r = await explain(p.statement, { pid: p.pid, display: "", display_text: p.passage, plain: p.plain, work: p.work, translator: p.translator, hide_in_distress: false });
    if (!r.ok) { console.log(id, "no note:", r.reason); continue; }
    record(`fidelity-explain ${id}`, EXPLAIN_MODEL, r.usage.input, r.usage.output);
    notes[id] = r.text;
    console.log(id, r.usage);
  }
  fs.writeFileSync(path.join(ROOT, "evals/explain/sonnet-api.json"), JSON.stringify({ writer: "sonnet-api", notes }, null, 1) + "\n");
} else if (kind === "rewrite") {
  const rewrites: { id: string; query: string }[] = [];
  for (const id of ids) {
    guardCap();
    const q = queries.find((x: { id: string }) => x.id === id);
    const r = await rewriteQuery(q.statement);
    if (!r) { console.log(id, "refused"); continue; }
    record(`fidelity-rewrite ${id}`, REWRITE_MODEL, r.usage.input, r.usage.output);
    rewrites.push({ id, query: r.text });
    console.log(id, r.usage);
  }
  fs.writeFileSync(path.join(ROOT, "evals/rewrites/haiku-api.json"), JSON.stringify({ rewrites }, null, 1) + "\n");
}
console.log(`API spend so far: $${spentSoFar().toFixed(5)}`);
