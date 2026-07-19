const STATUS_COPY = {
  pending: { label: "Awaiting review", tone: "text-muted" },
  approved: { label: "Approved", tone: "text-confirmed" },
  edited: { label: "Sent for edits", tone: "text-inference" },
  rejected: { label: "Rejected", tone: "text-conflict" },
};

export default function ReviewActionBar({ status, onApprove, onEdit, onReject }) {
  const copy = STATUS_COPY[status] || STATUS_COPY.pending;

  return (
    <div className="sticky bottom-0 left-0 right-0 border-t border-line bg-surface/95 backdrop-blur">
      <div className="mx-auto flex max-w-5xl flex-col gap-3 px-6 py-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2 text-sm">
          <span className="text-muted">Review status:</span>
          <span className={`font-medium ${copy.tone}`}>{copy.label}</span>
        </div>

        <div className="flex gap-2">
          <button
            onClick={onReject}
            className="rounded-md border border-line px-4 py-2 text-sm font-medium text-ink transition hover:border-conflict hover:text-conflict"
          >
            Reject
          </button>
          <button
            onClick={onEdit}
            className="rounded-md border border-line px-4 py-2 text-sm font-medium text-ink transition hover:border-inference hover:text-inference"
          >
            Edit
          </button>
          <button
            onClick={onApprove}
            className="rounded-md bg-brand px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-dark"
          >
            Approve
          </button>
        </div>
      </div>
    </div>
  );
}
