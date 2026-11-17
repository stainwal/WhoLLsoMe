// Saved passages, on the visitor's device only (Decisions, 16 Nov: no accounts). Stored in the browser's
// localStorage; never sent to the server. Only the passage is kept, never what the visitor typed.
// Every read and write is wrapped: storage can be blocked (private windows, strict settings).

export type ShownPassage = {
  pid: string;
  plain: string;
  text: string;
  location: string;
  work: string;
  translator: string;
  tradition: string;
};

export type SavedPassage = ShownPassage & { savedAt: string };

const KEY = "wl_saved_v1";
const MAX = 200;

export function readSaved(): SavedPassage[] {
  try {
    const raw = window.localStorage.getItem(KEY);
    const list = raw ? (JSON.parse(raw) as SavedPassage[]) : [];
    return Array.isArray(list) ? list.filter((p) => p && typeof p.pid === "string") : [];
  } catch {
    return [];
  }
}

function write(list: SavedPassage[]): boolean {
  try {
    window.localStorage.setItem(KEY, JSON.stringify(list.slice(0, MAX)));
    return true;
  } catch {
    return false;
  }
}

export function isSaved(pid: string): boolean {
  return readSaved().some((p) => p.pid === pid);
}

/** Adds the passage (newest first). Returns false if the browser won't store it. */
export function save(p: ShownPassage): boolean {
  const { pid, plain, text, location, work, translator, tradition } = p;
  const rest = readSaved().filter((s) => s.pid !== pid);
  return write([{ pid, plain, text, location, work, translator, tradition, savedAt: new Date().toISOString() }, ...rest]);
}

export function remove(pid: string): boolean {
  return write(readSaved().filter((p) => p.pid !== pid));
}
