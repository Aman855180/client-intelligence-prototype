import { useState } from "react";

export default function TranscriptInputPanel({ onSubmit, loading, error, onViewSample }) {
  const [text, setText] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    onSubmit(text);
  };

  return (
    <div className="mx-auto max-w-3xl px-6 py-16">
      <p className="text-xs font-semibold uppercase tracking-widest text-brand">
        Client Intelligence
      </p>
      <h1 className="mt-2 font-display text-3xl text-ink">Paste a coaching conversation</h1>
      <p className="mt-2 text-sm text-muted">
        The transcript is analyzed and returned as an evidence-grounded report — every
        finding is traceable back to the exact line it came from.
      </p>

      <form onSubmit={handleSubmit} className="mt-6">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Day 1&#10;Client: Slept only around 5 hours last night...&#10;Coach: ..."
          rows={14}
          className="w-full rounded-lg border border-line bg-surface p-4 font-mono text-[13px] leading-relaxed text-ink placeholder:text-faint focus:border-brand focus:outline-none"
        />

        {error && (
          <div className="mt-3 rounded-md border border-conflict/30 bg-conflict-soft px-4 py-3 text-sm text-conflict">
            {error}
          </div>
        )}

        <div className="mt-4 flex items-center justify-between">
          <span className="text-xs text-faint">
            {text.trim() ? `${text.trim().split(/\s+/).length} words` : "No text yet"}
          </span>
          <div className="flex items-center gap-3">
            {onViewSample && (
              <button
                type="button"
                onClick={onViewSample}
                className="text-xs font-medium text-muted underline underline-offset-2 hover:text-brand"
              >
                View sample report
              </button>
            )}
            <button
              type="submit"
              disabled={loading || !text.trim()}
              className="rounded-md bg-brand px-5 py-2.5 text-sm font-medium text-white transition hover:bg-brand-dark disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Analyzing…" : "Analyze conversation"}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
