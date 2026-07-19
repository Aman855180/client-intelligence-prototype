"""
FastAPI application for the FUME Client Intelligence prototype.

Single endpoint: POST /analyze
    Input:  { "conversation": "<raw transcript text>" }
    Output: ClientIntelligenceReport (validated, evidence-grounded JSON)

No auth, no database, no deployment config - intentionally minimal
per assignment scope. The interesting engineering is in the pipeline
(services/analysis_service.py), not the web layer.
"""

import logging

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()  # loads GEMINI_API_KEY etc. from a local .env file if present

from app.config import settings
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.analysis_service import AnalysisError, analyze_conversation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fume.client_intelligence")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Analyzes a coach-client conversation and returns an evidence-grounded, "
    "human-reviewable client intelligence report.",
)

# Wide-open CORS is fine for a prototype with no auth/deployment concerns.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Simple liveness check - not part of the assignment spec but
    useful for anyone running/demoing the prototype."""
    return {"status": "ok", "service": settings.APP_NAME, "version": settings.APP_VERSION}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    """
    Accepts a raw conversation transcript, runs it through the
    extraction + validation pipeline, and returns a structured,
    evidence-grounded ClientIntelligenceReport.

    Returns HTTP 422 if the request body is malformed (handled
    automatically by FastAPI/pydantic), and HTTP 502 if the LLM
    pipeline could not produce a schema-valid report after retries.
    """
    try:
        report = analyze_conversation(request.conversation)
        return AnalyzeResponse(success=True, data=report)
    except AnalysisError as exc:
        logger.error("Analysis failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"Failed to generate a valid client intelligence report: {exc}",
        ) from exc
    except Exception as exc:  # last-resort guard, never leak raw tracebacks
        logger.exception("Unexpected error in /analyze")
        raise HTTPException(status_code=500, detail="Internal server error.") from exc
