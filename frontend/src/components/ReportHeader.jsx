import ClassificationBadge from "./ClassificationBadge";
import ConfidenceBar from "./ConfidenceBar";

const NAV_ITEMS = [
  ["nutrition", "Nutrition"],
  ["exercise", "Exercise"],
  ["sleep", "Sleep"],
  ["water", "Water"],
  ["symptoms", "Symptoms"],
  ["stress", "Stress"],
  ["engagement", "Engagement"],
  ["barriers", "Barriers"],
  ["risks", "Risk Flags"],
  ["recommendations", "Recommendations"],
];

export default function ReportHeader({ report, onReset }) {
  const { period, weekly_summary: summary, client_id } = report;

  return (
    <header className="border-b border-line bg-surface">
      <div className="mx-auto max-w-5xl px-6 py-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-widest text-brand">
              Client Intelligence Report
            </p>
            <h1 className="mt-1 font-display text-2xl text-ink">
              {period.start_day} – {period.end_day}
            </h1>
            <p className="mt-0.5 text-xs text-faint">Client ID: {client_id}</p>
          </div>
          <button
            onClick={onReset}
            className="shrink-0 rounded-md border border-line px-3 py-1.5 text-xs font-medium text-muted hover:border-brand hover:text-brand"
          >
            New analysis
          </button>
        </div>

        <div className="mt-5 rounded-lg border border-line bg-bg p-4">
          <div className="flex items-start justify-between gap-3">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted">
              Weekly Summary
            </p>
            <ClassificationBadge classification={summary.classification} />
          </div>
          <p className="mt-2 font-display text-[17px] leading-relaxed text-ink">
            {summary.value}
          </p>
          <div className="mt-3">
            <ConfidenceBar confidence={summary.confidence} />
          </div>
        </div>

        <nav className="mt-5 flex flex-wrap gap-x-4 gap-y-1.5 text-xs">
          {NAV_ITEMS.map(([id, label]) => (
            <a key={id} href={`#${id}`} className="text-muted hover:text-brand">
              {label}
            </a>
          ))}
        </nav>
      </div>
    </header>
  );
}
