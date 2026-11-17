// Crisis check at runtime (Plan section 2.1, item 6; prompt and routing in ./crisis-prompt.ts).
// Two layers, as in the eval (evals/crisis.py): explicit phrases go straight to "crisis" with no model call;
// otherwise one Haiku call labels the statement. If the model can't answer (error, timeout, refusal or an
// unexpected reply) the result is "borderline": the helpline screen shows, with "Continue to passages".
// Failing towards the helpline screen is deliberate; failing towards passages could miss someone at risk.

import Anthropic from "@anthropic-ai/sdk";
import { CRISIS_PATTERNS, CRISIS_PROMPT_VERSION, CRISIS_SYSTEM, type CrisisLabel } from "./crisis-prompt";

export const CRISIS_MODEL = process.env.CRISIS_MODEL ?? "claude-haiku-5-5";

export type CrisisResult = {
  label: CrisisLabel;
  via: "pattern" | "model" | "fallback";
  promptVersion: string;
  usage?: { input: number; output: number };
};

let client: Anthropic | null = null;

/** The deterministic first layer alone: true if an explicit phrase matches (no model call). */
export function matchesCrisisPattern(statement: string): boolean {
  return CRISIS_PATTERNS.some((re) => re.test(statement));
}

export async function checkCrisis(statement: string): Promise<CrisisResult> {
  if (matchesCrisisPattern(statement)) {
    return { label: "crisis", via: "pattern", promptVersion: CRISIS_PROMPT_VERSION };
  }
  try {
    client ??= new Anthropic({ maxRetries: 1, timeout: 10_000 });
    const r = await client.messages.create({
      model: CRISIS_MODEL,
      max_tokens: 256,
      output_config: { effort: "low" },
      system: CRISIS_SYSTEM,
      messages: [{ role: "user", content: `<statement>\n${statement}\n</statement>` }],
    });
    const usage = { input: r.usage.input_tokens, output: r.usage.output_tokens };
    const word = r.content
      .flatMap((b) => (b.type === "text" ? [b.text] : []))
      .join("")
      .trim()
      .toLowerCase()
      .match(/^[a-z]+/)?.[0];
    if (r.stop_reason !== "refusal" && (word === "crisis" || word === "borderline" || word === "none")) {
      return { label: word, via: "model", promptVersion: CRISIS_PROMPT_VERSION, usage };
    }
    console.warn(`crisis: unexpected reply (stop=${r.stop_reason}); falling back to borderline`);
    return { label: "borderline", via: "fallback", promptVersion: CRISIS_PROMPT_VERSION, usage };
  } catch (err) {
    console.error(`crisis: model call failed (${err instanceof Anthropic.APIError ? err.status : "network"}); falling back to borderline`);
    return { label: "borderline", via: "fallback", promptVersion: CRISIS_PROMPT_VERSION };
  }
}
