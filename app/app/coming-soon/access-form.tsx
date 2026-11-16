"use client";

// Access-code form for testers. On success the page reloads and the proxy lets the visitor through.

import { useState } from "react";

const MESSAGES: Record<number, string> = {
  401: "That code didn't work.",
  429: "Too many tries. Please wait an hour and try again.",
};

export default function AccessForm() {
  const [code, setCode] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      const res = await fetch("/api/access", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code }),
      });
      if (res.ok) {
        window.location.reload();
        return;
      }
      setMessage(MESSAGES[res.status] ?? "Something went wrong. Please try again.");
    } catch {
      setMessage("Couldn't reach the site. Check your connection.");
    }
    setBusy(false);
  }

  return (
    <form onSubmit={submit} style={{ marginTop: "3rem", fontFamily: "system-ui, sans-serif", fontSize: "0.95rem" }}>
      <label htmlFor="access-code" style={{ display: "block", marginBottom: "0.4rem" }}>
        Have an access code?
      </label>
      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
        <input
          id="access-code"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          autoComplete="off"
          autoCapitalize="none"
          spellCheck={false}
          required
          style={{ flex: "1 1 12rem", padding: "0.6rem", fontSize: "1rem", minHeight: "44px" }}
        />
        <button type="submit" disabled={busy} style={{ padding: "0.6rem 1.2rem", fontSize: "1rem", minHeight: "44px" }}>
          {busy ? "Checking…" : "Enter"}
        </button>
      </div>
      <p role="status" aria-live="polite" style={{ minHeight: "1.5em", color: "#a33" }}>
        {message}
      </p>
    </form>
  );
}
