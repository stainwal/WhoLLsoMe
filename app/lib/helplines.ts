// Helplines on the crisis screen and the "Need help now?" page (Decisions, 16 Nov: India, US, UK and an
// international directory). Each entry was checked against its official page on the date given; re-check
// before launch (Day 32) and whenever this list changes. Only what the page itself says is shown.

export type Helpline = {
  country: string;
  name: string;
  numbers: { label: string; tel: string; sms?: boolean }[];
  note: string;
  source: string;
  checked: string;
};

export const HELPLINES: Helpline[] = [
  {
    country: "India",
    name: "Tele MANAS (Ministry of Health & Family Welfare)",
    numbers: [
      { label: "14416", tel: "14416" },
      { label: "1-800 891 4416", tel: "18008914416" },
    ],
    note: "Toll-free mental health support.",
    source: "https://telemanas.mohfw.gov.in/",
    checked: "2026-11-17",
  },
  {
    country: "United States",
    name: "988 Suicide & Crisis Lifeline",
    numbers: [{ label: "988", tel: "988", sms: true }],
    note: "Call or text, 24/7, free and confidential.",
    source: "https://988lifeline.org/",
    checked: "2026-11-17",
  },
  {
    country: "United Kingdom",
    name: "Samaritans",
    numbers: [{ label: "116 123", tel: "116123" }],
    note: "Free to call from any phone, 24 hours a day.",
    source: "https://www.samaritans.org/how-we-can-help/contact-samaritan/",
    checked: "2026-11-17",
  },
];

export const DIRECTORY = {
  name: "Find A Helpline",
  url: "https://findahelpline.com/",
  note: "Free, confidential helplines in other countries.",
  checked: "2026-11-17",
};
