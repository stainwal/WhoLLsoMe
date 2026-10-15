// API spend ledger: one line per real API call, so the session's actual spend can be reported
// (evals/results/api-spend.jsonl). Prices per 1M tokens, Claude API list prices (15 Oct 2026).
import fs from "node:fs";
import path from "node:path";
import nextEnv from "@next/env";
const { loadEnvConfig } = nextEnv;

export const ROOT = path.resolve(process.cwd(), "..");
loadEnvConfig(ROOT);

const PRICE: Record<string, [number, number]> = {
  "claude-haiku-5-5": [0.1, 0.5],
  "claude-sonnet-5-5": [2, 10],
  "claude-opus-5-5": [4, 20],
};

export function record(purpose: string, model: string, input: number, output: number): number {
  const [pi, po] = PRICE[model] ?? [0, 0];
  const usd = (input * pi + output * po) / 1e6;
  const line = { at: new Date().toISOString(), purpose, model, input, output, usd: Number(usd.toFixed(6)) };
  fs.appendFileSync(path.join(ROOT, "evals/results/api-spend.jsonl"), JSON.stringify(line) + "\n");
  return usd;
}

export function spentSoFar(): number {
  const f = path.join(ROOT, "evals/results/api-spend.jsonl");
  if (!fs.existsSync(f)) return 0;
  return fs.readFileSync(f, "utf8").trim().split("\n").filter(Boolean)
    .reduce((s, l) => s + JSON.parse(l).usd, 0);
}

export const SESSION_CAP_USD = 0.25;
export function guardCap() {
  if (spentSoFar() >= SESSION_CAP_USD) throw new Error(`API spend cap $${SESSION_CAP_USD} reached; stop and ask`);
}
