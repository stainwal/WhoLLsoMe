-- What the web app's server routes need (Day 22, 16 Nov 2026). Apply with:
--   .venv/bin/python backend/app_access.py apply      (safe to re-run)
--
-- The app connects as its own login role, whollsome_app, which can do exactly four things: read the
-- public_passages view, rank passages for a query vector, draw a Surprise passage and count rate-limit
-- hits. It cannot read the base tables, the restricted sources or anything else. The public (anon) key
-- gets none of this: every function below is revoked from public, anon and authenticated.

-- ---- rate limits (shared across all Vercel instances) ---------------------------------------------------
-- One row per key per fixed window. Keys are a salted hash of the visitor's IP plus the route, or a
-- "global:" key for the site-wide daily spend guard. No IP and nothing the person typed is stored.
create table if not exists rate_limits (
  key          text not null,
  window_start timestamptz not null,
  count        integer not null default 0,
  primary key (key, window_start)
);
alter table rate_limits enable row level security;
revoke all on rate_limits from public, anon, authenticated;

-- Counts one hit on p_key and says whether it is within p_max hits per p_window_seconds window.
create or replace function take_rate(p_key text, p_max integer, p_window_seconds integer)
returns table (allowed boolean, retry_after integer)
language plpgsql volatile security definer set search_path = public as $$
declare
  w timestamptz := to_timestamp(floor(extract(epoch from now()) / p_window_seconds) * p_window_seconds);
  c integer;
begin
  insert into rate_limits as r (key, window_start, count) values (p_key, w, 1)
  on conflict (key, window_start) do update set count = r.count + 1
  returning r.count into c;
  -- Housekeeping on about 1 call in 100: windows older than two days are never read again.
  if random() < 0.01 then
    delete from rate_limits where window_start < now() - interval '2 days';
  end if;
  return query select c <= p_max,
    case when c <= p_max then 0
         else greatest(1, ceil(extract(epoch from (w + make_interval(secs => p_window_seconds) - now())))::integer) end;
end $$;

-- ---- retrieval (Setup B, Decisions 15 Oct) ------------------------------------------------------------
-- Nearest passages to a query vector by cosine similarity, over what the public site may show to anyone:
-- no restricted or switched-off source, nothing hidden from distress (the same pool the evals scored;
-- evals/experiments.py, Corpus). Tone prior, near-duplicate collapse and the cut to 10 happen in the app
-- (app/lib/search.ts), exactly as in the evals.
create or replace function match_passages(q vector(1024), p_setup text, p_n integer)
returns table (pid text, near_group text, tone jsonb, similarity double precision)
language sql stable security definer set search_path = public as $$
  select p.pid, p.near_group, p.tags -> 'tone', 1 - (e.embedding <=> q)
  from passage_embeddings e
  join passages p on p.pid = e.pid
  join sources s on s.id = p.source_id
  where e.setup = p_setup and not s.restricted and s.active and not p.hide_in_distress
  order by e.embedding <=> q
  limit least(greatest(p_n, 1), 200)
$$;

-- ---- Surprise me (Plan section 2.1, item 4) -----------------------------------------------------------
-- One random passage of quotability 4-5, never one hidden from distress. No AI call.
create or replace function surprise_passage()
returns setof public_passages
language sql volatile security definer set search_path = public as $$
  select * from public_passages where quotability >= 4 and not hide_in_distress order by random() limit 1
$$;

revoke all on function take_rate(text, integer, integer) from public, anon, authenticated;
revoke all on function match_passages(vector, text, integer) from public, anon, authenticated;
revoke all on function surprise_passage() from public, anon, authenticated;

-- ---- the app's login role -----------------------------------------------------------------------------
-- Created without a password here; backend/app_access.py sets one and writes APP_DATABASE_URL to .env.
do $$ begin
  if not exists (select from pg_roles where rolname = 'whollsome_app') then
    create role whollsome_app login noinherit;
  end if;
end $$;
alter role whollsome_app set statement_timeout = '5s';
grant usage on schema public to whollsome_app;
grant select on public_passages to whollsome_app;
grant execute on function take_rate(text, integer, integer) to whollsome_app;
grant execute on function match_passages(vector, text, integer) to whollsome_app;
grant execute on function surprise_passage() to whollsome_app;

-- ---- spend log (Day 23) ---------------------------------------------------------------------------------
-- One row per paid API call made by the live site: when, which route, which model, tokens, cost. No text of
-- any kind (CLAUDE.md section 5, rule 5): the columns can't hold a statement. Scripts keep writing to
-- evals/results/api-spend.jsonl; app/scripts/spend.ts reports both together.
create table if not exists api_spend (
  id bigint generated always as identity primary key,
  at timestamptz not null default now(),
  route text not null check (route ~ '^[a-z-]{1,20}$'),
  model text not null check (model ~ '^[a-z0-9.-]{1,40}$'),
  input_tokens integer not null check (input_tokens >= 0),
  output_tokens integer not null check (output_tokens >= 0),
  usd numeric(12, 8) not null check (usd >= 0)
);
alter table api_spend enable row level security;
revoke all on api_spend from public, anon, authenticated;

-- The app can add rows through this function but can't read or change the table.
create or replace function record_spend(p_route text, p_model text, p_in integer, p_out integer, p_usd numeric)
returns void language sql volatile security definer set search_path = public as $$
  insert into api_spend (route, model, input_tokens, output_tokens, usd) values (p_route, p_model, p_in, p_out, p_usd)
$$;
revoke all on function record_spend(text, text, integer, integer, numeric) from public, anon, authenticated;
grant execute on function record_spend(text, text, integer, integer, numeric) to whollsome_app;
