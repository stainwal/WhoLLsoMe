// Database connection for server routes (Day 22). Connects as whollsome_app (backend/app.sql), a login that
// can only read public_passages and call three functions: match_passages, surprise_passage, take_rate.
// APP_DATABASE_URL points at Supabase's transaction pooler, so each serverless instance keeps one short-lived
// connection and prepared statements are off (the pooler doesn't keep them between transactions).

import postgres from "postgres";

let sql: postgres.Sql | null = null;

export function db(): postgres.Sql {
  if (!sql) {
    const url = process.env.APP_DATABASE_URL;
    if (!url) throw new Error("APP_DATABASE_URL is not set");
    sql = postgres(url, { prepare: false, max: 1, idle_timeout: 20, connect_timeout: 10, onnotice: () => {} });
  }
  return sql;
}
