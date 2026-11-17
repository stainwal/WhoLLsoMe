"use client";

// Site header on every page: name (home), Saved, and "Need help now?", always visible (Plan section 2, item 6).

import Link from "next/link";

export function SiteHeader({ onHome }: { onHome?: () => void }) {
  return (
    <header className="topbar">
      <a
        className="brand"
        href="/"
        onClick={onHome ? (e) => { e.preventDefault(); onHome(); } : undefined}
      >
        WhoLLsoMe
      </a>
      <nav className="topnav" aria-label="Site">
        <Link href="/saved">Saved</Link>
        <Link href="/help" className="help-link">Need help now?</Link>
      </nav>
    </header>
  );
}
