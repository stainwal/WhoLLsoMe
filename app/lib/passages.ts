// Passage lookup from the public_passages view (restricted and switched-off sources excluded;
// backend/schema.sql, backend/test_public_view.py), through the app's own database login (lib/db.ts).

import { db } from "./db";

export type Passage = {
  pid: string;
  display: string;        // location label, e.g. "Tao Te Ching 8"
  display_text: string;   // verbatim passage
  plain: string;          // stored plain-language version ("In plain words")
  work: string;
  translator: string;
  tradition: string;
  hide_in_distress: boolean;
};

const PID = /^[a-z0-9][a-z0-9-]{2,80}$/;
const COLUMNS = ["pid", "display", "display_text", "plain", "work", "translator", "tradition", "hide_in_distress"];

export async function getPassage(pid: string): Promise<Passage | null> {
  if (!PID.test(pid)) return null;
  const rows = await db()<Passage[]>`select ${db()(COLUMNS)} from public_passages where pid = ${pid}`;
  return rows[0] ?? null;
}

/** Several passages, returned in the order of `pids`; ids not in the view are skipped. */
export async function getPassages(pids: string[]): Promise<Passage[]> {
  if (!pids.length) return [];
  const rows = await db()<Passage[]>`select ${db()(COLUMNS)} from public_passages where pid in ${db()(pids)}`;
  const byId = new Map(rows.map((r) => [r.pid, r]));
  return pids.flatMap((p) => (byId.has(p) ? [byId.get(p)!] : []));
}

/** One random passage of quotability 4-5 that is never hidden from distress (Surprise me). */
export async function surprisePassage(): Promise<Passage | null> {
  const rows = await db()<Passage[]>`select ${db()(COLUMNS)} from surprise_passage()`;
  return rows[0] ?? null;
}

/** What the browser receives: the display fields only. */
export function publicView(p: Passage) {
  return {
    pid: p.pid,
    plain: p.plain,
    text: p.display_text,
    location: p.display,
    work: p.work,
    translator: p.translator,
    tradition: p.tradition,
  };
}
