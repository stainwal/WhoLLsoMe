// Crisis check through the real runtime code and API (Day 22): lib/crisis.ts on every test statement,
// both sets, including the 13 private crisis statements. Day 21's gate run used the same prompt on
// subagents; this confirms it through the path the live site uses.
// Writes ids and labels only, never statement text: evals/results/crisis-api-d22.json. Each call goes in
// the spend ledger.
//   cd app && npx tsx scripts/crisis-api.ts
import fs from "node:fs";
import path from "node:path";
import { record, ROOT } from "./ledger";
import { CRISIS_MODEL, checkCrisis } from "../lib/crisis";
import { SHOWS_HELPLINE } from "../lib/crisis-prompt";

type Row = { id: string; set: string; part: string; borderline: boolean; text: string };
const read = (f: string): Row[] =>
  fs.readFileSync(path.join(ROOT, f), "utf8").trim().split("\n").map((l) => JSON.parse(l));
const rows = [...read("evals/private/crisis.jsonl"), ...read("evals/human-set.jsonl"), ...read("evals/agent-set.jsonl")];

const out: { id: string; set: string; part: string; borderline: boolean; label: string; via: string }[] = [];
let usd = 0;
for (let i = 0; i < rows.length; i += 6) {
  const batch = rows.slice(i, i + 6);
  const res = await Promise.all(batch.map((r) => checkCrisis(r.text)));
  res.forEach((c, j) => {
    const r = batch[j];
    if (c.usage) usd += record("crisis-api-d22", CRISIS_MODEL, c.usage.input, c.usage.output);
    out.push({ id: r.id, set: r.set, part: r.part, borderline: r.borderline, label: c.label, via: c.via });
  });
}

const helpline = (o: (typeof out)[number]) => SHOWS_HELPLINE[o.label as keyof typeof SHOWS_HELPLINE];
const crisis = out.filter((o) => o.part === "crisis");
const look = (set: string) => out.filter((o) => o.part === "look-alike" && o.set === set);
const ordinary = out.filter((o) => o.part !== "crisis" && o.part !== "look-alike");
const summary = {
  crisis_recall: `${crisis.filter(helpline).length} of ${crisis.length}`,
  crisis_labels: Object.fromEntries(["crisis", "borderline", "none"].map((l) => [l, crisis.filter((o) => o.label === l).length])),
  false_crisis_human: `${look("human").filter(helpline).length} of ${look("human").length}`,
  false_crisis_agent: `${look("agent").filter(helpline).length} of ${look("agent").length}`,
  ordinary_shown_helpline: `${ordinary.filter(helpline).length} of ${ordinary.length}`,
  ordinary_ids_shown_helpline: ordinary.filter(helpline).map((o) => `${o.id}${o.borderline ? " [borderline]" : ""} ${o.label}`),
  fallbacks: out.filter((o) => o.via === "fallback").length,
  usd: Number(usd.toFixed(4)),
};
fs.writeFileSync(
  path.join(ROOT, "evals/results/crisis-api-d22.json"),
  JSON.stringify({ run_at: new Date().toISOString(), model: CRISIS_MODEL, rule: "v2 (crisis or borderline shows the helpline screen)", summary, labels: out.map(({ id, label, via }) => ({ id, label, via })) }, null, 1) + "\n",
);
console.log(JSON.stringify(summary, null, 1));
