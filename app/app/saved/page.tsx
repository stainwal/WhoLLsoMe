"use client";

// Saved passages: read from this device's storage (lib/saved.ts); nothing is fetched or sent.

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { readSaved, remove, type SavedPassage } from "@/lib/saved";
import { SiteHeader } from "../ui/header";
import { PassageBody } from "../ui/passage-view";

export default function SavedPage() {
  const [list, setList] = useState<SavedPassage[] | null>(null);
  const [msg, setMsg] = useState("");
  const headingRef = useRef<HTMLHeadingElement>(null);
  useEffect(() => setList(readSaved()), []);

  function drop(p: SavedPassage) {
    if (!remove(p.pid)) {
      setMsg("This browser won't let the site change saved passages.");
      return;
    }
    setList(readSaved());
    setMsg(`Removed: ${p.location}.`);
    headingRef.current?.focus();
  }

  return (
    <div className="page">
      <SiteHeader />
      <main>
        <h1 ref={headingRef} tabIndex={-1}>Saved</h1>
        <p className="lede">Kept on this device only. Clearing your browser&apos;s site data removes them.</p>
        <p className="visually-hidden" role="status" aria-live="polite">{msg}</p>
        {list === null ? null : list.length === 0 ? (
          <p>Nothing saved yet. Use <strong>Save</strong> under any passage. <Link href="/">Start a search</Link>.</p>
        ) : (
          <ul className="saved-list">
            {list.map((p, i) => (
              <li key={p.pid}>
                <h2 className="visually-hidden">{p.location}</h2>
                <PassageBody p={p} headingId={`saved${i}`} />
                <div className="actions">
                  <button type="button" onClick={() => drop(p)} aria-label={`Remove ${p.location} from Saved`}>
                    Remove
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </main>
    </div>
  );
}
