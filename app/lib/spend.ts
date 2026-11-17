// Spend log for the live site (Day 23): one row per paid API call in Supabase's api_spend table
// (backend/app.sql) with route, model, tokens and cost. Never any text. Scripts log to
// evals/results/api-spend.jsonl instead (scripts/ledger.ts); scripts/spend.ts reports both.

import { after } from "next/server";
import { db } from "./db";

// US dollars per 1M tokens, input and output. Claude API list prices (claude-api skill, cached 3 Nov 2026);
// voyage-4-lite at Voyage's list price, though the first 200M tokens are free (so real cost is $0 for now).
export const PRICE: Record<string, [number, number]> = {
  "claude-haiku-5-5": [0.1, 0.5],
  "claude-sonnet-5-5": [2, 10],
  "claude-opus-5-5": [4, 20],
  "voyage-4-lite": [0.02, 0],
};

export function cost(model: string, input: number, output: number): number {
  const [pi, po] = PRICE[model] ?? [0, 0];
  return (input * pi + output * po) / 1e6;
}

export type Usage = { input: number; output: number };

/** Records one call after the response has gone out, so it adds no wait. A failure is logged, not thrown. */
export function recordSpend(route: string, model: string, usage: Usage | undefined) {
  if (!usage) return;
  const usd = cost(model, usage.input, usage.output);
  after(async () => {
    try {
      await db()`select record_spend(${route}, ${model}, ${usage.input}, ${usage.output}, ${usd})`;
    } catch (err) {
      console.error(`spend: not recorded (${err instanceof Error ? err.name : "unknown"})`);
    }
  });
}
