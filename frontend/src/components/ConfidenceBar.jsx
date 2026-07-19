// Deliberately not a chart: a five-segment bar rendered with plain
// divs so confidence reads at a glance without implying false
// numerical precision from a bespoke chart component.

export default function ConfidenceBar({ confidence = 0 }) {
  const segments = 5;
  const filled = Math.round(confidence * segments);
  const pct = Math.round(confidence * 100);

  let tone = "bg-missing";
  if (confidence >= 0.8) tone = "bg-confirmed";
  else if (confidence >= 0.5) tone = "bg-inference";
  else if (confidence > 0) tone = "bg-conflict";

  return (
    <div className="flex items-center gap-2">
      <div className="flex gap-0.5" role="img" aria-label={`Confidence ${pct} percent`}>
        {Array.from({ length: segments }).map((_, i) => (
          <span
            key={i}
            className={`h-1.5 w-3.5 rounded-sm ${i < filled ? tone : "bg-line"}`}
          />
        ))}
      </div>
      <span className="font-mono text-xs text-muted tabular-nums">{pct}%</span>
    </div>
  );
}
