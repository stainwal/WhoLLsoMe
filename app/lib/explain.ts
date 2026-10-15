// Explain: one Claude call that says how a passage speaks to what the person wrote (Plan section 1, item 3).
// The passage is looked up server-side by its id, never taken from the client, so the endpoint can't be
// used as a general-purpose model proxy.

import Anthropic from "@anthropic-ai/sdk";
import { EXPLAIN_SYSTEM, EXPLAIN_PROMPT_VERSION, explainUserMessage } from "./explain-prompt";
import type { Passage } from "./passages";

// Sonnet 5.5, chosen by experiment 5 (Day 20: rubric pass 97.5% vs Haiku 85%); EXPLAIN_MODEL overrides it.
export const EXPLAIN_MODEL = process.env.EXPLAIN_MODEL ?? "claude-sonnet-5-5";
export const MAX_STATEMENT_CHARS = 2000;
const MAX_TOKENS = 1024; // includes any thinking at low effort; the note itself is under 90 words

let client: Anthropic | null = null;
function getClient(): Anthropic {
  // Reads ANTHROPIC_API_KEY from the environment; never logged.
  client ??= new Anthropic({ maxRetries: 2, timeout: 30_000 });
  return client;
}

export type ExplainResult =
  | { ok: true; text: string; model: string; promptVersion: string; usage: { input: number; output: number } }
  | { ok: false; reason: "refused" | "empty" | "too_long" };

export async function explain(statement: string, passage: Passage, model = EXPLAIN_MODEL): Promise<ExplainResult> {
  const response = await getClient().messages.create({
    model,
    max_tokens: MAX_TOKENS,
    output_config: { effort: "low" },
    system: EXPLAIN_SYSTEM,
    messages: [
      {
        role: "user",
        content: explainUserMessage({
          statement,
          passage: passage.display_text,
          plain: passage.plain,
          work: passage.work,
          translator: passage.translator,
        }),
      },
    ],
  });

  if (response.stop_reason === "refusal") return { ok: false, reason: "refused" };
  if (response.stop_reason === "max_tokens") return { ok: false, reason: "too_long" };
  const text = response.content
    .flatMap((b) => (b.type === "text" ? [b.text] : []))
    .join("")
    .trim();
  if (!text) return { ok: false, reason: "empty" };
  return {
    ok: true,
    text,
    model: response.model,
    promptVersion: EXPLAIN_PROMPT_VERSION,
    usage: { input: response.usage.input_tokens, output: response.usage.output_tokens },
  };
}
