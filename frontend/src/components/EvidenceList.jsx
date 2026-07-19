export default function EvidenceList({ evidence = [] }) {
  if (!evidence.length) {
    return <p className="text-xs text-faint italic">No source quote available.</p>;
  }

  return (
    <ul className="space-y-2">
      {evidence.map((item, i) => (
        <li
          key={i}
          className="border-l-2 border-line pl-3 py-0.5"
        >
          <p className="font-mono text-[13px] leading-relaxed text-ink/90">
            &ldquo;{item.quote}&rdquo;
          </p>
          <p className="mt-1 text-[11px] uppercase tracking-wide text-faint">
            {item.day}
            {item.speaker ? ` · ${item.speaker}` : ""}
          </p>
        </li>
      ))}
    </ul>
  );
}
