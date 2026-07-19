"""
Analysis orchestration service.

Owns the flow: raw transcript -> LLM call -> parse JSON -> validate
against the Pydantic schema -> (retry with correction note on failure)
-> return a validated ClientIntelligenceReport.

This is where hallucination/format failures are caught before they
ever reach the API response. Nothing here trusts the LLM output
until it has passed pydantic validation.
"""

import json
import re
import uuid
from datetime import datetime, timezone

from pydantic import ValidationError

from app.config import settings
from app.models.schemas import ClientIntelligenceReport
from app.services.llm_service import LLMServiceError, llm_service


class AnalysisError(Exception):
    """Raised when the transcript could not be turned into a valid report
    after all retry attempts."""


def _strip_markdown_fences(text: str) -> str:
    """
    Defensive cleanup: even though the prompt forbids markdown fences,
    models occasionally add them anyway. Strip ```json ... ``` wrappers
    if present, without altering the JSON content itself.
    """
    fenced = re.match(r"^```(?:json)?\s*(.*)```\s*$", text.strip(), re.DOTALL)
    if fenced:
        return fenced.group(1).strip()
    return text.strip()


def _extract_json_object(text: str) -> str:
    """
    Extracts the outermost JSON object from the text as a fallback in
    case the model added any stray characters before/after the braces.
    """
    text = _strip_markdown_fences(text)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in LLM response.")
    return text[start : end + 1]


def analyze_conversation(transcript: str) -> ClientIntelligenceReport:
    """
    Runs the full extraction + validation pipeline with bounded retries.
    Raises AnalysisError if a valid report cannot be produced.
    """
    correction_note = ""
    last_error = ""

    for attempt in range(settings.MAX_LLM_RETRIES + 1):
        try:
            raw_text = llm_service.extract_client_intelligence(
                transcript=transcript, correction_note=correction_note
            )
        except LLMServiceError as exc:
            # Upstream/network failure - not worth retrying with a
            # correction note, surface immediately.
            raise AnalysisError(str(exc)) from exc

        try:
            json_str = _extract_json_object(raw_text)
            parsed = json.loads(json_str)
        except (ValueError, json.JSONDecodeError) as exc:
            last_error = f"Response was not valid JSON: {exc}"
            correction_note = last_error
            continue

        # Backfill fields the LLM isn't responsible for generating
        # (deterministic metadata), rather than trusting the model to
        # invent IDs/timestamps.
        parsed.setdefault("report_id", f"report_{uuid.uuid4().hex[:12]}")
        parsed.setdefault("client_id", "anonymized_client")

        try:
            report = ClientIntelligenceReport.model_validate(parsed)
            return report
        except ValidationError as exc:
            last_error = f"Schema validation failed: {exc}"
            correction_note = last_error
            continue

    raise AnalysisError(
        f"Failed to produce a valid client intelligence report after "
        f"{settings.MAX_LLM_RETRIES + 1} attempt(s). Last error: {last_error}"
    )
