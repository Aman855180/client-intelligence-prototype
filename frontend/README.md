# FUME Client Intelligence — Frontend Prototype

> Part of the combined `fume-client-intelligence` repo. See the [root README](../README.md) to run backend + frontend together.

React + Tailwind dashboard that calls `POST /analyze` and renders the
evidence-grounded report for coach review.

## Project structure

```
fume-frontend/
├── index.html
├── vite.config.js              # dev proxy: /analyze -> http://127.0.0.1:8000
├── tailwind.config.js          # design tokens (colors, fonts)
├── src/
│   ├── main.jsx
│   ├── App.jsx                 # top-level state: input -> loading -> report -> review
│   ├── api/analyzeClient.js    # POST /analyze fetch wrapper
│   ├── utils/classification.js # single source of truth for classification colors/labels
│   ├── data/sampleReport.json  # demo data for the "View sample report" shortcut
│   └── components/
│       ├── TranscriptInputPanel.jsx   # paste transcript + submit
│       ├── ReportHeader.jsx           # period, weekly summary, section nav
│       ├── ReportBody.jsx             # renders every category section
│       ├── CategorySection.jsx        # groups GradedFieldCards under a heading
│       ├── GradedFieldCard.jsx        # value + classification + confidence + evidence
│       ├── FindingCard.jsx            # for barriers / risk flags / recommendations
│       ├── ClassificationBadge.jsx
│       ├── ConfidenceBar.jsx          # plain segmented bar, not a chart
│       ├── EvidenceList.jsx           # verbatim quotes, mono font
│       └── ReviewActionBar.jsx        # sticky Approve / Edit / Reject bar
```

## Setup

```bash
cd fume-frontend
npm install
cp .env.example .env
npm run dev
```

Runs at `http://localhost:5173`. Requires the FastAPI backend running at
`http://127.0.0.1:8000` (the Vite dev server proxies `/analyze` to it —
see `vite.config.js`).

No backend handy? Click **"View sample report"** on the input screen —
it loads `src/data/sampleReport.json`, which is shaped exactly like a
real `/analyze` response, so every card renders identically.

## Design notes

- **Classification color is the page's visual language, not decoration.**
  Every card — regardless of whether it's a single metric or a risk flag
  — uses the same five-color mapping (`src/utils/classification.js`):
  teal = confirmed fact, blue = client-reported, amber = AI inference,
  gray = missing, rust = conflicting. A coach learns the mapping once
  and can scan the whole report by color.
- **Evidence quotes are set in monospace** with a left border, distinct
  from the rest of the UI type, to visually signal "this is exact
  source text," not a paraphrase.
- **No charts.** Confidence is a five-segment bar built from plain
  `<div>`s — deliberately not a chart library, per the assignment's
  "no fake charts" instruction, since a single 0–1 score doesn't
  warrant real chart machinery.
- **Review actions are global and sticky at the bottom** of the report,
  matching the assignment spec exactly (Approve / Edit / Reject),
  rather than per-card — per-card actions would fight with "every card
  shows confidence/evidence/classification" for visual attention.
- Fonts: Fraunces (headings only, used sparingly) + Inter (UI/body) +
  IBM Plex Mono (evidence, confidence %) — chosen to avoid the generic
  cream/terracotta or dark/neon AI-template look.

## Known limitations (prototype scope)

- Approve/Edit/Reject only update local UI state — there's no database,
  so nothing persists on refresh (matches the backend's "no database"
  scope).
- "Edit" currently just sets review status; a production version would
  open an inline editor per section and log the diff, per the original
  architecture's human-review design.
