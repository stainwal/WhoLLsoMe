"use client";

// The whole visitor flow on one page (Days 23-24): home -> results (one passage at a time, Next / Back
// through up to 10, Explain, Save, Report), Surprise me, and the helpline screen for a clear crisis.
// What the visitor types stays in this page's memory only: it is sent to /api/search and /api/explain and
// nowhere else, never put in the URL, never saved on the device (only saved passages are).

import { useCallback, useEffect, useRef, useState } from "react";
import type { ShownPassage } from "@/lib/saved";
import { ConsentNote } from "./consent";
import { SiteHeader } from "./header";
import { HelpContent } from "./help";
import { ExplainBlock, PassageBody, ReportBlock, SaveButton, type ExplainState } from "./passage-view";

const MAX_CHARS = 2000; // same as the server (lib/explain.ts)
const SLOW_SEARCH_MS = 4000;
const SLOW_EXPLAIN_MS = 8000;

type View =
  | { kind: "home" }
  | { kind: "searching"; slow: boolean }
  | { kind: "results"; passages: ShownPassage[]; index: number; gentle: boolean }
  | { kind: "surprise"; passage: ShownPassage | null; loading: boolean }
  | { kind: "helpline" };

type ApiResult = { ok: boolean; status: number; data: Record<string, unknown>; retryAfter: number };

async function call(url: string, init?: RequestInit): Promise<ApiResult> {
  try {
    const res = await fetch(url, { ...init, headers: { "Content-Type": "application/json" }, cache: "no-store" });
    const data = (await res.json().catch(() => ({}))) as Record<string, unknown>;
    return { ok: res.ok, status: res.status, data, retryAfter: Number(res.headers.get("Retry-After") ?? 0) };
  } catch {
    return { ok: false, status: 0, data: { error: "network" }, retryAfter: 0 };
  }
}

/** A plain-language message for every failure the routes can return. */
function errorMessage(r: ApiResult, what: "search" | "explain" | "surprise"): string {
  const e = r.data.error;
  if (r.status === 0) return "Couldn't reach the site. Check your connection and try again.";
  if (e === "rate_limited") {
    const mins = Math.max(1, Math.ceil(r.retryAfter / 60));
    return `You've used this a lot in the last hour. Please try again in about ${mins} minute${mins === 1 ? "" : "s"}.`;
  }
  if (e === "busy_today") return "The site has reached its limit for today. Please come back tomorrow.";
  if (e === "busy") return "The service is busy right now. Please try again in a minute.";
  if (e === "bad_request") return `Please write something about what's on your mind (up to ${MAX_CHARS.toLocaleString()} characters).`;
  if (e === "unknown_passage") return "This passage can't be explained.";
  if (e === "no_explanation") return "No explanation could be written for this one. Try another passage.";
  if (what === "explain") return "The explanation service isn't answering right now. Please try again in a moment.";
  return "Something went wrong on our side. Please try again in a moment.";
}

export default function App() {
  const [statement, setStatement] = useState("");
  const [view, setView] = useState<View>({ kind: "home" });
  const [error, setError] = useState("");
  const [explains, setExplains] = useState<Record<string, ExplainState>>({});
  const headingRef = useRef<HTMLHeadingElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const searched = useRef(""); // the statement the current results answer (Explain uses this one)

  // The phone's Back gesture returns to the home screen instead of leaving the site.
  const goHome = useCallback(() => {
    setView({ kind: "home" });
    setTimeout(() => inputRef.current?.focus(), 0);
  }, []);
  useEffect(() => {
    const onPop = () => goHome();
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, [goHome]);
  const enter = (v: View) => {
    if (view.kind === "home" || view.kind === "searching") window.history.pushState({ wl: v.kind }, "");
    setView(v);
  };

  // Move keyboard and screen-reader focus to the new content's heading.
  const viewKey = view.kind === "results" ? `r${view.index}` : view.kind;
  useEffect(() => {
    if (view.kind !== "home" && view.kind !== "searching") headingRef.current?.focus();
  }, [viewKey]); // eslint-disable-line react-hooks/exhaustive-deps

  async function search(e: React.FormEvent) {
    e.preventDefault();
    const text = statement.trim();
    if (!text) {
      setError("Please write something first.");
      inputRef.current?.focus();
      return;
    }
    setError("");
    setView({ kind: "searching", slow: false });
    const slow = setTimeout(() => setView((v) => (v.kind === "searching" ? { kind: "searching", slow: true } : v)), SLOW_SEARCH_MS);
    const r = await call("/api/search", { method: "POST", body: JSON.stringify({ statement: text }) });
    clearTimeout(slow);
    if (r.status === 401) return window.location.reload(); // access cookie gone: back to the holding page
    if (!r.ok) {
      setView({ kind: "home" });
      setError(errorMessage(r, "search"));
      return;
    }
    searched.current = text;
    setExplains({});
    const passages = (r.data.passages as ShownPassage[] | undefined) ?? [];
    const crisis = r.data.crisis;
    // Only a clear crisis shows the helpline screen (crisis-v2, 17 Nov); "borderline" gets passages, with
    // "Need help now?" on every screen.
    if (crisis === "crisis") {
      enter({ kind: "helpline" });
      return;
    }
    if (!passages.length) {
      setView({ kind: "home" });
      setError("Nothing close enough was found. Try saying a little more about what's happening.");
      return;
    }
    enter({ kind: "results", passages, index: 0, gentle: crisis === "borderline" });
  }

  async function surprise() {
    setError("");
    enter({ kind: "surprise", passage: view.kind === "surprise" ? view.passage : null, loading: true });
    const r = await call("/api/surprise");
    if (r.status === 401) return window.location.reload();
    if (!r.ok) {
      setView({ kind: "home" });
      setError(errorMessage(r, "surprise"));
      return;
    }
    setView({ kind: "surprise", passage: r.data.passage as ShownPassage, loading: false });
  }

  async function explain(pid: string) {
    setExplains((m) => ({ ...m, [pid]: { kind: "loading", slow: false } }));
    const slow = setTimeout(
      () => setExplains((m) => (m[pid]?.kind === "loading" ? { ...m, [pid]: { kind: "loading", slow: true } } : m)),
      SLOW_EXPLAIN_MS,
    );
    const r = await call("/api/explain", { method: "POST", body: JSON.stringify({ statement: searched.current, pid }) });
    clearTimeout(slow);
    if (r.status === 401) return window.location.reload();
    if (r.ok && r.data.crisis === "crisis") {
      enter({ kind: "helpline" });
      return;
    }
    if (r.ok && typeof r.data.text === "string") {
      setExplains((m) => ({ ...m, [pid]: { kind: "done", text: r.data.text as string, label: String(r.data.label ?? "AI-generated explanation") } }));
      return;
    }
    setExplains((m) => ({ ...m, [pid]: { kind: "error", message: errorMessage(r, "explain") } }));
  }

  return (
    <div className="page">
      <SiteHeader onHome={goHome} />

      <main>
        {(view.kind === "home" || view.kind === "searching") && (
          <>
            <h1>What&apos;s on your mind?</h1>
            <p className="lede">
              Say how you feel and get passages from the world&apos;s wisdom literature, quoted exactly, each with a
              plain-words version. Not therapy or advice.
            </p>
            <ConsentNote />
            <form onSubmit={search} noValidate>
              <label htmlFor="statement">Your words</label>
              <textarea
                id="statement"
                ref={inputRef}
                value={statement}
                onChange={(e) => setStatement(e.target.value)}
                maxLength={MAX_CHARS}
                aria-describedby="statement-hint form-status"
                disabled={view.kind === "searching"}
              />
              <p className="hint" id="statement-hint">
                Nothing you write is stored on this site. {statement.length > MAX_CHARS - 200 && `${MAX_CHARS - statement.length} characters left.`}
              </p>
              <div className="actions">
                <button type="submit" className="primary" disabled={view.kind === "searching"}>
                  Find passages
                </button>
                <button type="button" onClick={surprise} disabled={view.kind === "searching"}>
                  Surprise me
                </button>
              </div>
              <div className="status" id="form-status" role="status" aria-live="polite">
                {view.kind === "searching" && (
                  <p>
                    <span className="spinner" aria-hidden="true" />
                    {view.slow
                      ? "Still looking. The first search after a quiet spell takes a few seconds longer."
                      : "Finding passages…"}
                  </p>
                )}
                {error && <p className="error">{error}</p>}
              </div>
            </form>
          </>
        )}

        {view.kind === "results" && (() => {
          const p = view.passages[view.index];
          const n = view.passages.length;
          const go = (i: number) => setView({ ...view, index: i });
          return (
            <>
              <h1 ref={headingRef} tabIndex={-1} className="position-heading">
                Passage {view.index + 1} of {n}
              </h1>
              {view.gentle && view.index === 0 && (
                // A "borderline" result (crisis-v2): passages, with support one tap away. Not a wall.
                <p className="gentle">
                  If things feel very heavy right now, you don&apos;t have to carry them alone.{" "}
                  <a href="/help">Talk to someone</a>.
                </p>
              )}
              <PassageBody p={p} headingId={`p${view.index}`} />
              <div className="actions">
                <SaveButton p={p} />
              </div>
              <div style={{ marginTop: "1rem" }}>
                <ExplainBlock state={explains[p.pid] ?? { kind: "idle" }} onExplain={() => explain(p.pid)} />
              </div>
              <nav className="nav" aria-label="Passages">
                <button type="button" onClick={() => go(view.index - 1)} disabled={view.index === 0}>
                  ← Back
                </button>
                <span className="position" aria-hidden="true">{view.index + 1} of {n}</span>
                <button type="button" onClick={() => go(view.index + 1)} disabled={view.index === n - 1}>
                  Next →
                </button>
              </nav>
              <button type="button" className="link" onClick={() => window.history.back()}>
                Start again
              </button>
              <ReportBlock pid={p.pid} explained={explains[p.pid]?.kind === "done"} />
            </>
          );
        })()}

        {view.kind === "surprise" && (
          <>
            <h1 ref={headingRef} tabIndex={-1}>A passage for you</h1>
            {view.passage ? (
              <>
                <PassageBody p={view.passage} headingId="s" />
                <div className="actions">
                  <SaveButton p={view.passage} />
                  <button type="button" onClick={surprise} disabled={view.loading}>
                    {view.loading ? "Finding another…" : "Another"}
                  </button>
                </div>
                <p className="hint">To get an explanation, write what&apos;s on your mind and search instead.</p>
                <ReportBlock pid={view.passage.pid} explained={false} searched={false} />
              </>
            ) : (
              <p role="status"><span className="spinner" aria-hidden="true" />Finding a passage…</p>
            )}
            <p><button type="button" className="link" onClick={() => window.history.back()}>Back to start</button></p>
          </>
        )}

        {view.kind === "helpline" && (
          // Shown only for a clear crisis (crisis-v2): helplines, no passages, no option to continue.
          <section className="notice" aria-labelledby="help-heading">
            <h1 id="help-heading" ref={headingRef} tabIndex={-1}>You don&apos;t have to carry this alone</h1>
            <p>What you wrote sounds serious. Please talk to someone now; it can help to say it out loud.</p>
            <HelpContent />
            <div className="actions">
              <button type="button" onClick={() => window.history.back()}>Back to start</button>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
