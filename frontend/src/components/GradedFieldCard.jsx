import ClassificationBadge from "./ClassificationBadge";
import ConfidenceBar from "./ConfidenceBar";
import EvidenceList from "./EvidenceList";

function renderValue(value) {
  if (value === null || value === undefined || value === "") {
    return <span className="text-faint italic">No data reported for this period.</span>;
  }
  if (Array.isArray(value)) return value.join(", ");
  return String(value);
}

export default function GradedFieldCard({ label, field }) {
  const evidenceCount = field?.evidence?.length || 0;

  return (
    <div className="rounded-lg border border-line bg-surface p-4">
      <div className="flex items-start justify-between gap-3">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted">{label}</p>
        <ClassificationBadge classification={field.classification} />
      </div>

      <p className="mt-2 text-sm leading-relaxed text-ink">{renderValue(field.value)}</p>

      <div className="mt-3">
        <ConfidenceBar confidence={field.confidence} />
      </div>

      <details className="mt-3 group">
        <summary className="flex cursor-pointer select-none items-center gap-1 text-xs font-medium text-muted hover:text-brand">
          <span className="transition-transform group-open:rotate-90">›</span>
          Evidence ({evidenceCount})
        </summary>
        <div className="mt-2 pl-3">
          <EvidenceList evidence={field.evidence} />
        </div>
      </details>
    </div>
  );
}
