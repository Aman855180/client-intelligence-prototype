// Single source of truth mapping backend classification values to
// display label + Tailwind color tokens. Every card in the app reads
// from this so the color language stays consistent end to end.

export const CLASSIFICATION_META = {
  confirmed_fact: {
    label: "Confirmed Fact",
    text: "text-confirmed",
    bg: "bg-confirmed-soft",
    dot: "bg-confirmed",
    border: "border-confirmed/30",
  },
  client_reported: {
    label: "Client Reported",
    text: "text-reported",
    bg: "bg-reported-soft",
    dot: "bg-reported",
    border: "border-reported/30",
  },
  ai_inference: {
    label: "AI Inference",
    text: "text-inference",
    bg: "bg-inference-soft",
    dot: "bg-inference",
    border: "border-inference/30",
  },
  missing_information: {
    label: "Missing Information",
    text: "text-missing",
    bg: "bg-missing-soft",
    dot: "bg-missing",
    border: "border-missing/30",
  },
  conflicting_reports: {
    label: "Conflicting Reports",
    text: "text-conflict",
    bg: "bg-conflict-soft",
    dot: "bg-conflict",
    border: "border-conflict/30",
  },
};

export function classificationMeta(classification) {
  return CLASSIFICATION_META[classification] || CLASSIFICATION_META.missing_information;
}

export const SEVERITY_META = {
  high: { label: "High", text: "text-conflict", bg: "bg-conflict-soft" },
  medium: { label: "Medium", text: "text-inference", bg: "bg-inference-soft" },
  low: { label: "Low", text: "text-muted", bg: "bg-missing-soft" },
};

export function severityMeta(severity) {
  return SEVERITY_META[severity] || SEVERITY_META.low;
}
