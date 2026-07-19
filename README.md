# FUME — Client Intelligence Platform (Prototype)

GenAI Client Intelligence mini-case submission. A FastAPI backend that
turns a raw coach-client transcript into an evidence-grounded,
schema-validated JSON report, and a React + Tailwind dashboard that
renders it for coach review (Approve / Edit / Reject).

```
fume-client-intelligence/
├── backend/     FastAPI service — POST /analyze
├── frontend/    React + Tailwind dashboard
└── README.md    (this file)
```

Each folder has its own README with full details. This file only
covers running them together.

## Run both together

You need two terminals — one process per service. No deployment
config, no database, no auth, per the assignment's scope.

**Terminal 1 — backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then add your GEMINI_API_KEY
uvicorn app.main:app --reload
```
Runs at `http://127.0.0.1:8000`. Check `http://127.0.0.1:8000/health`.

**Terminal 2 — frontend**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
Runs at `http://localhost:5173`. Its dev server already proxies
`/analyze` requests to `http://127.0.0.1:8000` (see
`frontend/vite.config.js`), so the two just work together with no
extra config once both are running.

No backend running yet? Open the frontend and click **"View sample
report"** on the landing screen — it renders a fully-shaped sample
response (`frontend/src/data/sampleReport.json`) so you can explore
the UI immediately.

Or use the convenience script from the repo root, which starts both
and stops both together on Ctrl+C:
```bash
./start-dev.sh
```
(First run `pip install -r backend/requirements.txt` inside a venv and
`npm install` inside `frontend/` once, as above — the script just
launches both, it doesn't install dependencies.)

## How the two pieces fit together

```
Coach pastes transcript (frontend)
        │
        ▼
POST /analyze  ───────────────►  backend/app/main.py
                                        │
                                        ▼
                          backend/app/services/analysis_service.py
                          (calls LLM → parses JSON → validates
                           against backend/app/models/schemas.py →
                           retries with correction note on failure)
                                        │
                                        ▼
                     200 { success, data: ClientIntelligenceReport }
                                        │
                                        ▼
        frontend renders ReportHeader + ReportBody, one card per
        finding, each showing value / classification / confidence /
        evidence — then the coach hits Approve / Edit / Reject
```

The frontend never has to guess at the response shape — `AnalyzeResponse`
in `backend/app/models/schemas.py` and the card components in
`frontend/src/components/` are built against the exact same JSON
schema, so a validated backend response always renders cleanly.

## Submission deliverables

The system design, the production prompt/workflow, the JSON schema,
three hallucination/failure scenarios, and a short technical note are
in [`docs/`](docs/):

- [`docs/Prompt_Workflow.md`](docs/Prompt_Workflow.md) — end-to-end
  workflow, architecture diagram, prompt design, Gemini call details,
  validation/retry logic
- [`docs/JSON_Schema.md`](docs/JSON_Schema.md) — the full schema
  enforced by the backend, field-by-field
- [`docs/Failure_Scenarios.md`](docs/Failure_Scenarios.md) — three
  hallucination/failure scenarios with current mitigations and future
  improvements
- [`docs/Solution_Note.md`](docs/Solution_Note.md) — what was built,
  key assumptions, design decisions, limitations, and why Gemini was
  selected
- [`docs/Demo_Video_Script.md`](docs/Demo_Video_Script.md) — a 3–5
  minute demo script

This repo is the implementation those documents describe — not a
separate thing from it.
