// Guard checks with no model calls (Day 22): the shared rate limit in Supabase allows the limit and refuses
// the next with a Retry-After; visitors are counted apart; the visitor key never contains the raw IP;
// Turnstile is off until its secret is set; the access gate fails closed and accepts only the right cookie.
//   cd app && npx tsx scripts/test-guards.ts
import { randomUUID } from "node:crypto";
import "./ledger"; // loads the repository's .env
import { db } from "../lib/db";
import { accessToken, gateOn, hasAccess } from "../lib/gate";
import { checkLimits, VISITOR_LIMITS, verifyTurnstile, visitorKey } from "../lib/guards";

let fails = 0;
const check = (name: string, ok: boolean) => { fails += ok ? 0 : 1; console.log(`${ok ? "PASS" : "FAIL"}  ${name}`); };

const v1 = `test-${randomUUID()}`, v2 = `test-${randomUUID()}`;
const max = VISITOR_LIMITS.surprise.max;
const results = [];
for (let i = 0; i <= max; i++) results.push(await checkLimits("surprise", v1));
check(`${max} allowed per hour (shared store)`, results.slice(0, max).every((r) => r.allowed));
check(`${max + 1}th refused with a Retry-After`, !results[max].allowed && results[max].retryAfterSec > 0);
check("another visitor unaffected", (await checkLimits("surprise", v2)).allowed);
// The test keys are removed by take_rate's two-day housekeeping.

const key = visitorKey(new Headers({ "x-forwarded-for": "203.0.113.7" }));
check("visitor key is a hash, not the IP", /^[0-9a-f]{32}$/.test(key) && !key.includes("203"));

const secret = process.env.TURNSTILE_SECRET_KEY;
delete process.env.TURNSTILE_SECRET_KEY;
check("Turnstile off without a secret", await verifyTurnstile(undefined));
process.env.TURNSTILE_SECRET_KEY = "test";
check("Turnstile on: missing token refused", !(await verifyTurnstile(undefined)));
if (secret) process.env.TURNSTILE_SECRET_KEY = secret; else delete process.env.TURNSTILE_SECRET_KEY;

const gate = process.env.SITE_GATE, code = process.env.ACCESS_CODE;
process.env.SITE_GATE = "on";
const token = await accessToken();
check("gate: right cookie lets in", token !== null && (await hasAccess(token)));
check("gate: no cookie refused", !(await hasAccess(undefined)));
check("gate: wrong cookie refused", !(await hasAccess("0".repeat(64))));
delete process.env.SITE_GATE;
check("gate: on when SITE_GATE is missing", gateOn());
delete process.env.ACCESS_CODE;
check("gate: shut when ACCESS_CODE is missing", !(await hasAccess(token ?? "x")));
process.env.SITE_GATE = "off";
check("gate: SITE_GATE=off opens the site", await hasAccess(undefined));
if (gate) process.env.SITE_GATE = gate;
if (code) process.env.ACCESS_CODE = code;

await db().end();
process.exit(fails ? 1 : 0);
