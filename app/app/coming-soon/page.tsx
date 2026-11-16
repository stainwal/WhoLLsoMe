// Holding page shown for every URL until launch (lib/gate.ts, proxy.ts). Plain on purpose: the visual
// pass is Day 27.

import AccessForm from "./access-form";

export const metadata = { title: "WhoLLsoMe: coming soon", robots: { index: false, follow: false } };

export default function ComingSoon() {
  return (
    <main style={{ maxWidth: 32 + "rem", margin: "0 auto", padding: "15vh 1rem 2rem", fontFamily: "Georgia, serif", lineHeight: 1.5 }}>
      <h1 style={{ fontWeight: "normal", fontSize: "2rem", margin: 0 }}>WhoLLsoMe</h1>
      <p style={{ fontSize: "1.15rem" }}>
        Passages from the world&apos;s wisdom literature, for whatever you&apos;re carrying. Coming soon.
      </p>
      <AccessForm />
    </main>
  );
}
