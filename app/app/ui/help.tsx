// Helplines, used on the crisis screen and the "Need help now?" page. Numbers come from lib/helplines.ts,
// each checked against its official page (date shown).

import { DIRECTORY, HELPLINES } from "@/lib/helplines";

const fmt = (iso: string) =>
  new Date(iso + "T12:00:00Z").toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });

export function HelpContent() {
  return (
    <>
      <p>
        <strong>If you are in immediate danger, call your local emergency number now.</strong>
      </p>
      <p>These services are free to call. You can talk to someone today:</p>
      <ul className="help-list">
        {HELPLINES.map((h) => (
          <li key={h.country}>
            <p className="label">{h.country}</p>
            <p className="help-name">{h.name}</p>
            <p className="help-numbers">
              {h.numbers.map((n, i) => (
                <span key={n.tel}>
                  {i > 0 && " or "}
                  <a href={`tel:${n.tel}`} className="help-number">{n.label}</a>
                  {n.sms && <> (call or <a href={`sms:${n.tel}`}>text</a>)</>}
                </span>
              ))}
            </p>
            <p className="hint">{h.note}</p>
          </li>
        ))}
        <li>
          <p className="label">Anywhere else</p>
          <p className="help-name">
            <a href={DIRECTORY.url} target="_blank" rel="noopener noreferrer">{DIRECTORY.name}</a>
          </p>
          <p className="hint">{DIRECTORY.note}</p>
        </li>
      </ul>
      <p className="hint">Numbers checked against each service&apos;s own website on {fmt(HELPLINES[0].checked)}.</p>
    </>
  );
}
