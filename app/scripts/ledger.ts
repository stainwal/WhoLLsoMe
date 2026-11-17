// API spend ledger for scripts: one line per real API call (evals/results/api-spend.jsonl): when, purpose,
// model, tokens, cost; never any text. The live site logs to Supabase instead (lib/spend.ts, same prices);
// scripts/spend.ts reports both.
import fs from "node:fs";
import path from "node:path";
import nextEnv from "@next/env";
import { cost } from "../lib/spend";
const { loadEnvConfig } = nextEnv;

export const ROOT = path.resolve(process.cwd(), "..");
loadEnvConfig(ROOT);
const LEDGER = path.join(ROOT, "evals/results/api-spend.jsonl");

export function record(purpose: string, model: string, input: number, output: number): number {
  const usd = cost(model, input, output);
  const line = { at: new Date().toISOString(), purpose, model, input, output, usd: Number(usd.toFixed(6)) };
  fs.appendFileSync(LEDGER, JSON.stringify(line) + "\n");
  return usd;
}

/** Script spend since `since` (ISO time or date); everything if omitted. */
export function spentSoFar(since = ""): number {
  if (!fs.existsSync(LEDGER)) return 0;
  return fs.readFileSync(LEDGER, "utf8").trim().split("\n").filter(Boolean)
    .map((l) => JSON.parse(l)).filter((r) => r.at >= since).reduce((s, r) => s + r.usd, 0);
}

// Per-session cap set by Shailesh ($0.30 on 17 Nov), counted from SESSION_START (an ISO date or time).
export const SESSION_CAP_USD = Number(process.env.SESSION_CAP_USD ?? 0.3);
export function guardCap() {
  const spent = spentSoFar(process.env.SESSION_START ?? new Date().toISOString().slice(0, 10));
  if (spent >= SESSION_CAP_USD) throw new Error(`API spend cap $${SESSION_CAP_USD} reached; stop and ask`);
}
