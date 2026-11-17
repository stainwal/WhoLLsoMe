// "Need help now?" page, linked from every screen.

import { SiteHeader } from "../ui/header";
import { HelpContent } from "../ui/help";

export const metadata = { title: "Need help now? · WhoLLsoMe" };

export default function HelpPage() {
  return (
    <div className="page">
      <SiteHeader />
      <main>
        <h1>Need help now?</h1>
        <p className="lede">
          WhoLLsoMe offers passages to reflect on. It isn&apos;t therapy or a crisis service. If things feel too
          heavy, please reach out to people trained to help.
        </p>
        <HelpContent />
      </main>
    </div>
  );
}
