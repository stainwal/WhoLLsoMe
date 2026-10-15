// Setup B, step 1: turn what the person typed into a search query (one Haiku call). The query is combined
// with the statement before embedding (evals/experiments.py, "when+rewrite-concat").

import Anthropic from "@anthropic-ai/sdk";
import { REWRITE_SYSTEM } from "./rewrite-prompt";

export const REWRITE_MODEL = process.env.REWRITE_MODEL ?? "claude-haiku-5-5";

let client: Anthropic | null = null;

export async function rewriteQuery(statement: string, model = REWRITE_MODEL) {
  client ??= new Anthropic({ maxRetries: 2, timeout: 15_000 });
  const r = await client.messages.create({
    model,
    max_tokens: 512,
    output_config: { effort: "low" },
    system: REWRITE_SYSTEM,
    messages: [{ role: "user", content: `<statement>\n${statement}\n</statement>` }],
  });
  if (r.stop_reason === "refusal") return null;
  const text = r.content.flatMap((b) => (b.type === "text" ? [b.text] : [])).join("").trim();
  return { text, usage: { input: r.usage.input_tokens, output: r.usage.output_tokens } };
}
