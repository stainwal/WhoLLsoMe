-- WhoLLsoMe database schema (Day 16, 12 Oct 2026). Postgres on Supabase, with pgvector.
-- Apply with: .venv/bin/python backend/load.py schema   (safe to re-run)

create extension if not exists vector;

-- One row per source folder in corpus/source/. Credits shown in the app come from here
-- (docs/Corpus-Policy.md sections 2 and 3).
create table if not exists sources (
  id          text primary key,           -- folder name, e.g. 'tao-te-ching-legge'
  tradition   text not null,
  work        text not null,
  translator  text not null,
  licence     text not null,
  restricted  boolean not null default false,  -- copyrighted or GRAY: never shown on the public site until cleared
  active      boolean not null default true    -- pipeline/sources.toml switch
);

-- One row per passage a user can be shown (status keep or no-distress).
create table if not exists passages (
  pid            text primary key,          -- e.g. 'tao-001-p01'
  source_id      text not null references sources(id),
  display        text not null,             -- location label, e.g. 'Tao Te Ching 8'
  display_text   text not null,             -- verbatim passage, transcription fixes applied
  plain          text not null,             -- stored plain-language version ("In plain words")
  core_idea      text not null,
  quotability    smallint not null check (quotability between 1 and 5),
  complete       boolean not null,
  hide_in_distress boolean not null,        -- status no-distress: never shown to someone in distress
  near_group     text,                      -- related passages; never two from one group in an answer
  words          integer not null,
  faith          text not null,             -- faith framing tag
  tags           jsonb not null             -- feelings, themes, situations, tone, keywords, when_helps, safety
);
create index if not exists passages_source on passages (source_id);

-- Embeddings kept apart from passages so experiments (Plan section 4.4) can store several setups side by
-- side: 'setup' names the model and what was embedded, e.g. 'voyage-4-lite/text+plain'.
create table if not exists passage_embeddings (
  pid        text not null references passages(pid) on delete cascade,
  setup      text not null,
  embedding  vector(1024) not null,
  primary key (pid, setup)
);

-- Row-level security on, with no policies: the public anon key can read nothing. The app's server
-- routes use the service key, which bypasses RLS.
alter table sources enable row level security;
alter table passages enable row level security;
alter table passage_embeddings enable row level security;

-- Public read path (13 Oct 2026). The anon (public) key reads one view and nothing else: shown passages
-- with their credits, minus restricted sources and sources switched off. Table privileges are revoked
-- outright, so the base tables stay closed even if a row-level policy is added by mistake later.
revoke all on sources, passages, passage_embeddings from anon, authenticated;
alter default privileges for role postgres in schema public revoke all on tables from anon, authenticated;

-- Runs with its owner's rights (not security_invoker), so anon needs no grant on the tables underneath.
-- Any search function added later must also revoke execute from public and anon unless it is meant to be public.
create or replace view public_passages with (security_barrier = true) as
  select p.pid, p.source_id, p.display, p.display_text, p.plain, p.core_idea, p.quotability, p.complete,
         p.hide_in_distress, p.near_group, p.words, p.faith, p.tags,
         s.tradition, s.work, s.translator, s.licence
  from passages p join sources s on s.id = p.source_id
  where not s.restricted and s.active;

revoke all on public_passages from anon, authenticated;
grant select on public_passages to anon, authenticated;
