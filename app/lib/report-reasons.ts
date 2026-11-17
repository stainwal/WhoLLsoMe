// Reasons a visitor can give for "Report this response". The ids match the check on reports.reason in
// backend/app.sql; change both together.
export const REPORT_REASONS = [
  { id: "doesnt_fit", label: "Doesn't fit what I wrote" },
  { id: "upsetting", label: "Harmful or upsetting" },
  { id: "text_error", label: "Mistake in the text or credit" },
  { id: "explain_wrong", label: "The explanation is wrong or unhelpful" },
  { id: "other", label: "Something else" },
] as const;

export type ReportReason = (typeof REPORT_REASONS)[number]["id"];
export const isReportReason = (r: string): r is ReportReason => REPORT_REASONS.some((x) => x.id === r);
