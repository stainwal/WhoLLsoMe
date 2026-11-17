"use client";

// Consent notice on the home screen until the visitor dismisses it (remembered on this device only).
// Short on purpose: most visitors are trying the project out. Says what happens to what they type.

import { useEffect, useState } from "react";

const KEY = "wl_consent_v1";

export function ConsentNote() {
  const [show, setShow] = useState(false);
  useEffect(() => {
    try {
      setShow(window.localStorage.getItem(KEY) !== "ok");
    } catch {
      setShow(true);
    }
  }, []);
  if (!show) return null;

  function dismiss() {
    try {
      window.localStorage.setItem(KEY, "ok");
    } catch {
      // storage blocked: the note simply shows again next visit
    }
    setShow(false);
  }

  return (
    <section className="consent" aria-label="Before you start">
      <p>
        <strong>Before you start:</strong> WhoLLsoMe is a personal project, not therapy or a crisis service. What
        you type is sent to AI services (Anthropic and Voyage AI) to find and explain passages. This site doesn&apos;t
        store it.
      </p>
      <button type="button" onClick={dismiss}>OK, got it</button>
    </section>
  );
}
