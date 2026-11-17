"use client";

// One passage: plain version first ("In plain words", stored, AI-written offline), then the verbatim
// original with its location, credited to work and translator. Below it, Save and (when there is a
// statement to explain against) the Explain button.

import { useEffect, useState } from "react";
import { isSaved, remove, save, type ShownPassage } from "@/lib/saved";

export type ExplainState =
  | { kind: "idle" }
  | { kind: "loading"; slow: boolean }
  | { kind: "done"; text: string; label: string }
  | { kind: "error"; message: string };

export function PassageBody({ p, headingId }: { p: ShownPassage; headingId?: string }) {
  return (
    <div className="passage-grid">
      <section className="card" aria-labelledby={headingId ? `${headingId}-plain` : undefined}>
        <p className="label" id={headingId ? `${headingId}-plain` : undefined}>In plain words</p>
        <p className="plain">{p.plain}</p>
        <p className="hint">Written with AI and checked; the original is the source.</p>
      </section>
      <section className="card" aria-labelledby={headingId ? `${headingId}-orig` : undefined}>
        <p className="label" id={headingId ? `${headingId}-orig` : undefined}>The original · {p.location}</p>
        <blockquote className="original" style={{ margin: 0 }}>{p.text}</blockquote>
        <p className="credit">
          <cite>{p.work}</cite> · {p.translator}
        </p>
      </section>
    </div>
  );
}

export function SaveButton({ p }: { p: ShownPassage }) {
  const [saved, setSaved] = useState(false);
  const [msg, setMsg] = useState("");
  useEffect(() => setSaved(isSaved(p.pid)), [p.pid]);

  function toggle() {
    const ok = saved ? remove(p.pid) : save(p);
    if (!ok) {
      setMsg("This browser won't let the site save. Saving needs site storage turned on.");
      return;
    }
    setSaved(!saved);
    setMsg(saved ? "Removed from Saved." : "Saved on this device.");
  }

  return (
    <>
      <button type="button" onClick={toggle} aria-pressed={saved}>
        {saved ? "Saved ✓" : "Save"}
      </button>
      <span className="visually-hidden" role="status" aria-live="polite">{msg}</span>
      {msg.startsWith("This browser") && <p className="error">{msg}</p>}
    </>
  );
}

export function ExplainBlock({ state, onExplain }: { state: ExplainState; onExplain: () => void }) {
  return (
    <div>
      {state.kind !== "done" && (
        <button type="button" onClick={onExplain} disabled={state.kind === "loading"}>
          {state.kind === "loading" ? "Explaining…" : "Explain how this applies to me"}
        </button>
      )}
      <div className="status" role="status" aria-live="polite">
        {state.kind === "loading" && (
          <p>
            <span className="spinner" aria-hidden="true" />
            {state.slow ? "Still writing — this can take up to half a minute." : "Writing an explanation…"}
          </p>
        )}
        {state.kind === "error" && <p className="error">{state.message}</p>}
      </div>
      {state.kind === "done" && (
        <section className="explain" aria-label="AI-generated explanation">
          <p className="label">{state.label}</p>
          <p style={{ margin: 0 }}>{state.text}</p>
        </section>
      )}
    </div>
  );
}
