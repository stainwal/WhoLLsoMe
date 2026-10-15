// Guard checks with no model calls: the rate limit allows 20 per window and refuses the 21st; the visitor
// key never contains the raw IP; Turnstile is off until its secret is set, then refuses a missing token.
import { EXPLAIN_LIMIT, MemoryRateLimiter, verifyTurnstile, visitorKey } from "../lib/guards";

let fails = 0;
const check = (name: string, ok: boolean) => { fails += ok ? 0 : 1; console.log(`${ok ? "PASS" : "FAIL"}  ${name}`); };

const lim = new MemoryRateLimiter(EXPLAIN_LIMIT.max, EXPLAIN_LIMIT.windowMs);
const results = [];
for (let i = 0; i < 21; i++) results.push(await lim.take("v1"));
check("20 Explains allowed in an hour", results.slice(0, 20).every((r) => r.allowed));
check("21st refused with a Retry-After", !results[20].allowed && results[20].retryAfterSec > 0);
check("another visitor unaffected", (await lim.take("v2")).allowed);
const key = visitorKey(new Headers({ "x-forwarded-for": "203.0.113.7" }));
check("visitor key is a hash, not the IP", /^[0-9a-f]{32}$/.test(key) && !key.includes("203"));
delete process.env.TURNSTILE_SECRET_KEY;
check("Turnstile off without a secret", await verifyTurnstile(undefined));
process.env.TURNSTILE_SECRET_KEY = "test";
check("Turnstile on: missing token refused", !(await verifyTurnstile(undefined)));
process.exit(fails ? 1 : 0);
