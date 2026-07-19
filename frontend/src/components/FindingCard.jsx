import ClassificationBadge from "./ClassificationBadge";
import ConfidenceBar from "./ConfidenceBar";
import EvidenceList from "./EvidenceList";
import { severityMeta } from "../utils/classification";

// tag: optional { label, tone } e.g. { label: "High severity", tone: "high" }
export default function FindingCard({ text, classification, confidence, evidence, tag, meta }) {
  return (
    <div className="rounded-lg border border-line bg-surface p-4">
      <div className="flex flex-wrap items-center gap-2">
        <ClassificationBadge classification={classification} />
        {tag && (
          <span
            className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ${severityMeta(tag.toneKey).bg} ${severityMeta(tag.toneKey).text}`}
          >
            {tag.label}
          </span>
        )}
        {meta && <span className="text-xs text-faint">{meta}</span>}
      </div>

      <p className="mt-2 text-sm leading-relaxed text-ink">{text}</p>

      <div className="mt-3">
        <ConfidenceBar confidence={confidence} />
      </div>

      <details className="mt-3 group">
        <summary className="flex cursor-pointer select-none items-center gap-1 text-xs font-medium text-muted hover:text-brand">
          <span className="transition-transform group-open:rotate-90">›</span>
          Evidence ({evidence?.length || 0})
        </summary>
        <div className="mt-2 pl-3">
          <EvidenceList evidence={evidence} />
        </div>
      </details>
    </div>
  );
}
