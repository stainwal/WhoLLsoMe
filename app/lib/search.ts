// Retrieval at runtime: Setup B (Decisions, 15 Oct), the same ranking the evals scored as "B/haiku" in
// evals/experiments.py:
//   1. Haiku rewrites the statement into a search query (./rewrite.ts).
//   2. statement + "\n\n" + query is embedded with voyage-4-lite (input_type "query", 1024 dimensions).
//   3. The 200 nearest passages by cosine similarity, against passage text + plain version + "when this
//      helps" (setup voyage-4-lite/text+plain+when), over passages anyone may be shown (match_passages).
//   4. score = similarity + 0.2 x mean tone prior of the passage's tone tags.
//   5. Best first; one passage per near-duplicate group; the top 10.
// If the rewrite fails, the statement alone is embedded (step 2 without the query) and the rest is unchanged.

import { db } from "./db";
import { rewriteQuery } from "./rewrite";

export const SETUP = "voyage-4-lite/text+plain+when";
const EMBED_MODEL = "voyage-4-lite";
const CANDIDATES = 200;
const TONE_WEIGHT = 0.2;
export const RESULTS = 10;

// Tone prior, measured on the agent golden set only (evals/experiments.py, TONE; 13 Oct). Keep in step.
const TONE: Record<string, number> = {
  stern: -0.19, challenging: -0.1, contemplative: -0.05, practical: -0.01, steadying: 0.01,
  companioning: 0.06, affirming: 0.07, uplifting: 0.13, consoling: 0.21,
};

export const EMBED_MODEL_ID = EMBED_MODEL;

export async function embedQuery(text: string): Promise<number[]> {
  return (await embedQueryWithUsage(text)).vector;
}

/** The query vector and the tokens Voyage counted (for the spend log). */
export async function embedQueryWithUsage(text: string): Promise<{ vector: number[]; tokens: number }> {
  const key = process.env.VOYAGE_API_KEY;
  if (!key) throw new Error("VOYAGE_API_KEY is not set");
  const res = await fetch("https://api.voyageai.com/v1/embeddings", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({ input: [text], model: EMBED_MODEL, input_type: "query", output_dimension: 1024 }),
    signal: AbortSignal.timeout(8000),
  });
  if (!res.ok) throw new Error(`embedding failed: HTTP ${res.status}`);
  const data = (await res.json()) as { data: { embedding: number[] }[]; usage?: { total_tokens?: number } };
  return { vector: data.data[0].embedding, tokens: data.usage?.total_tokens ?? 0 };
}

type Candidate = { pid: string; near_group: string | null; tone: string[] | null; similarity: number };

/** Steps 3-5 for a query vector: up to RESULTS passage ids, best first. */
export async function rank(vector: number[]): Promise<{ pid: string; score: number }[]> {
  const q = `[${vector.join(",")}]`;
  const rows = await db()<Candidate[]>`
    select pid, near_group, tone, similarity from match_passages(${q}::vector, ${SETUP}, ${CANDIDATES})`;
  const scored = rows
    .map((r) => {
      const tones = r.tone ?? [];
      const prior = tones.length ? tones.reduce((s, t) => s + (TONE[t] ?? 0), 0) / tones.length : 0;
      return { pid: r.pid, group: r.near_group, score: r.similarity + TONE_WEIGHT * prior };
    })
    .sort((a, b) => b.score - a.score);
  const seen = new Set<string>();
  const out: { pid: string; score: number }[] = [];
  for (const s of scored) {
    if (s.group) {
      if (seen.has(s.group)) continue;
      seen.add(s.group);
    }
    out.push({ pid: s.pid, score: s.score });
    if (out.length === RESULTS) break;
  }
  return out;
}

/** The rewrite for step 1, or null if it failed; never throws. */
export async function safeRewrite(statement: string) {
  try {
    const r = await rewriteQuery(statement);
    return r?.text ? r : null;
  } catch (err) {
    console.warn(`search: rewrite failed (${err instanceof Error ? err.name : "unknown"}); searching on the statement alone`);
    return null;
  }
}

export function queryText(statement: string, rewrite: string | null): string {
  return rewrite ? `${statement}\n\n${rewrite}` : statement;
}
