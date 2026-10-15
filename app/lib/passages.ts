// Passage lookup through Supabase's public REST API with the publishable key. The key can read only the
// public_passages view (restricted sources excluded; backend/schema.sql, backend/test_public_view.py).

export type Passage = {
  pid: string;
  display: string;
  display_text: string;
  plain: string;
  work: string;
  translator: string;
  hide_in_distress: boolean;
};

const PID = /^[a-z0-9][a-z0-9-]{2,80}$/;

export async function getPassage(pid: string): Promise<Passage | null> {
  if (!PID.test(pid)) return null;
  const url = new URL("/rest/v1/public_passages", process.env.SUPABASE_URL);
  url.searchParams.set("select", "pid,display,display_text,plain,work,translator,hide_in_distress");
  url.searchParams.set("pid", `eq.${pid}`);
  const res = await fetch(url, {
    headers: { apikey: process.env.SUPABASE_ANON_KEY ?? "" },
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`passage lookup failed: HTTP ${res.status}`);
  const rows = (await res.json()) as Passage[];
  return rows[0] ?? null;
}
