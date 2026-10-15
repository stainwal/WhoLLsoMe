// (a) One test call to confirm ANTHROPIC_API_KEY works. Prints no secrets.
import Anthropic from "@anthropic-ai/sdk";
import { guardCap, record } from "./ledger";

guardCap();
const client = new Anthropic();
const model = "claude-haiku-5-5";
const r = await client.messages.create({
  model,
  max_tokens: 64,
  output_config: { effort: "low" },
  messages: [{ role: "user", content: "Reply with the single word: ready" }],
});
const text = r.content.flatMap((b) => (b.type === "text" ? [b.text] : [])).join("");
const usd = record("api-check", model, r.usage.input_tokens, r.usage.output_tokens);
console.log({ model: r.model, stop_reason: r.stop_reason, text, usage: r.usage, usd });
