# FUME Client Intelligence — Backend Prototype

> Part of the combined `fume-client-intelligence` repo. See the [root README](../README.md) to run backend + frontend together.

Minimal FastAPI backend for the GenAI Client Intelligence mini-case.
One endpoint, no auth, no database, no deployment config — by design.

## Project structure

```
fume-backend/
├── app/
│   ├── main.py                     # FastAPI app + POST /analyze endpoint
│   ├── config.py                   # env-based settings
│   ├── models/
│   │   └── schemas.py              # Pydantic request/response + report schema
│   ├── prompts/
│   │   └── system_prompt.py        # production system prompt (extraction+synthesis)
│   └── services/
│       ├── llm_service.py          # thin Google Gemini (google-genai SDK) wrapper
│       └── analysis_service.py     # orchestration: call -> parse -> validate -> retry
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

**1. Create a Gemini API key.**
Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey), sign in,
and generate a key. Free tier is enough to run this prototype.

**2. Copy `.env.example` to `.env` and add your key.**
```bash
cd fume-backend
cp .env.example .env
```
Open `.env` and replace `YOUR_API_KEY` with the key from step 1:
```
GEMINI_API_KEY=your_actual_key_here
```

**3. Install dependencies.**
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

**4. Run the backend.**
```bash
uvicorn app.main:app --reload
```
Server starts at `http://127.0.0.1:8000`. Interactive docs at `/docs`.

**5. Run the frontend** (separate terminal — see `../frontend/README.md`,
or the [root README](../README.md) to run both together):
```bash
cd ../frontend
npm install
npm run dev
```
No frontend changes were needed for this provider swap — it still just
calls `POST /analyze` and renders whatever comes back.

## Usage

```bash
curl -X POST http://127.0.0.1:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"conversation": "Day 1\nClient: Slept 5 hours...\nCoach: ..."}'
```

Response shape:

```json
{
  "success": true,
  "data": { "client_id": "...", "weekly_summary": {...}, "risk_flags": [...], "...": "..." },
  "error": null
}
```

On failure (LLM error, or the model could not produce a schema-valid
report after retries), you'll get a `502` with `success: false` semantics
communicated via HTTP status + `detail` message — the API never returns
a 200 with unvalidated or partially-invented data.

## How hallucination control is enforced here (not just prompted)

1. **Structured parsing, not string trust.** The raw LLM text is parsed
   as JSON; if that fails, we retry with a correction note rather than
   guessing at repair.
2. **Pydantic schema validation.** `ClientIntelligenceReport` enforces:
   - every field has a valid `classification` enum value
   - `confidence` is bounded 0.0–1.0
   - **every `GradedField` with a non-"missing_information" classification
     must include at least one evidence item** (see `GradedField`'s
     validator in `schemas.py`) — a claim with no evidence is rejected,
     not passed through.
   - `risk_flags` and `conflicting_reports` have minimum evidence-count
     requirements (1 and 2 respectively) baked into the schema itself.
3. **Bounded retries with corrective feedback.** If parsing or validation
   fails, the specific error is fed back to the model on the next attempt
   (`MAX_LLM_RETRIES`, default 2) instead of silently accepting bad output
   or crashing on the first failure.
4. **No silent fallback data.** If all retries are exhausted, the endpoint
   returns a `502` — it never fabricates a "safe-looking" default report.

## Notes / scope

- No authentication, no persistence layer, no deployment tooling — matches
  the assignment's explicit scope.
- `report_id` and `client_id` are backfilled deterministically in
  `analysis_service.py` rather than trusted from the LLM, since these are
  identifiers, not analytical findings.

## LLM provider

Currently: **Google Gemini** (`gemini-2.5-flash` by default, via the
official `google-genai` SDK), reading `GEMINI_API_KEY` from the
environment. Previously Ollama (local), and before that Anthropic
Claude — each swap only ever touched `app/services/llm_service.py` and
`app/config.py`; the endpoint, schema, prompt, and validation logic
have stayed the same across all three.

`llm_service.py` handles, with everything logged via the standard
`logging` module so failures are diagnosable from backend logs alone:
- **Gemini API errors** (`google.genai.errors.APIError` and its
  `ClientError`/`ServerError` subclasses) — bad key, bad model name,
  quota exhaustion, Gemini-side failures.
- **Timeouts** — configurable via `GEMINI_TIMEOUT_SECONDS` (default 120s).
- **Malformed/empty responses** — an empty response body raises
  immediately rather than being passed downstream as an empty string.
- **Invalid JSON on the first attempt** — retried once internally
  (a fresh Gemini call, not a correction-note re-prompt) before
  falling through to `analysis_service.py`'s existing
  retry-with-correction-note loop, which still applies on top.
- **Markdown code fences** (` ```json ... ``` `) — stripped defensively,
  even though `response_mime_type="application/json"` already asks
  Gemini not to include them.
