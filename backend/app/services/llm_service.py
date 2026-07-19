"""
LLM service: thin wrapper around the Google Gemini API (google-genai SDK).

Kept deliberately dumb - this module's only job is "send prompt,
get text back." Parsing, validation and the correction-note retry
loop live in services/analysis_service.py so each module has one
responsibility, and analysis_service.py did not need any changes
for this provider swap.

Provider history: Anthropic Claude -> Ollama (local) -> Gemini (this
version). The public interface (LLMService.extract_client_intelligence,
LLMServiceError) has stayed identical across all three swaps.
"""

import json
import logging
import re

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from app.config import settings
from app.prompts.system_prompt import SYSTEM_PROMPT

logger = logging.getLogger("fume.llm_service")


class LLMServiceError(Exception):
    """Raised when the LLM call itself fails (auth, network, timeout, bad response, etc.)."""


class LLMService:
    def __init__(self) -> None:
        if not settings.GEMINI_API_KEY:
            # Fail loudly at call-time rather than crashing import for
            # environments (e.g. tests) that stub this class out.
            self._client = None
        else:
            self._client = genai.Client(
                api_key=settings.GEMINI_API_KEY,
                http_options=types.HttpOptions(
                    timeout=settings.GEMINI_TIMEOUT_SECONDS * 1000  # SDK expects milliseconds
                ),
            )

    def extract_client_intelligence(self, transcript: str, correction_note: str = "") -> str:
        """
        Sends the transcript (and an optional correction note, used on
        retry after a validation failure) to Gemini and returns the
        raw text response, with markdown fences stripped if present.

        If the first response isn't parseable JSON, retries the raw
        Gemini call once before giving up - this is in addition to,
        and independent of, analysis_service.py's own retry-with-
        correction-note loop.
        """
        if self._client is None:
            raise LLMServiceError(
                "GEMINI_API_KEY is not configured. Set it as an environment variable."
            )

        user_message = f"TRANSCRIPT:\n{transcript}"
        if correction_note:
            user_message += (
                "\n\nNOTE: Your previous response failed validation for the "
                f"following reason: {correction_note}\n"
                "Re-generate the FULL JSON object, fixing this issue. "
                "Return ONLY the corrected JSON object, nothing else."
            )

        raw_text = self._call_gemini(user_message)
        cleaned = self._strip_code_fences(raw_text)

        if not self._is_valid_json(cleaned):
            logger.warning(
                "Gemini response was not valid JSON on first attempt "
                "(len=%d chars); retrying once. Preview: %r",
                len(cleaned),
                cleaned[:200],
            )
            raw_text = self._call_gemini(user_message, is_retry=True)
            cleaned = self._strip_code_fences(raw_text)

        return cleaned

    def _build_config(self, disable_thinking: bool = True) -> "types.GenerateContentConfig":
        kwargs = dict(
            system_instruction=SYSTEM_PROMPT,
            temperature=settings.LLM_TEMPERATURE,
            max_output_tokens=settings.LLM_MAX_TOKENS,
            # Gemini-level constraint that the output must be syntactically
            # valid JSON. This is an API parameter, not a prompt change -
            # the prompt's own JSON-only instruction is untouched.
            response_mime_type="application/json",
        )
        if disable_thinking:
            # Several Gemini models spend a large, variable chunk of
            # max_output_tokens on internal "thinking" before writing the
            # actual answer - for a long JSON schema like ours, that can
            # consume the whole budget and truncate the real output into
            # invalid JSON. This task needs no reasoning, so thinking is
            # disabled to keep the full token budget for the JSON itself.
            # Not every model family accepts this field (e.g. some Gemini 3
            # Pro variants can't disable thinking at all), so callers fall
            # back to a config without it if Gemini rejects the request.
            kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=0)
        return types.GenerateContentConfig(**kwargs)

    def _call_gemini(self, user_message: str, is_retry: bool = False) -> str:
        """Makes a single Gemini API call and returns the raw text, with
        provider-specific errors normalized into LLMServiceError and
        logged with enough detail to debug from the backend logs alone."""
        config = self._build_config(disable_thinking=True)
        try:
            response = self._invoke(user_message, config, is_retry)
        except genai_errors.ClientError as exc:
            # Some model families (e.g. Gemini 3 Pro) reject thinking_budget
            # entirely rather than ignoring it - retry once without it
            # before treating this as a real failure. Any other ClientError
            # (bad key, bad/retired model name, quota) is logged and wrapped
            # the same way _invoke wraps every other APIError.
            if "thinking" in str(getattr(exc, "message", str(exc))).lower():
                logger.warning(
                    "Model %s rejected thinking_config; retrying without it.",
                    settings.GEMINI_MODEL,
                )
                config = self._build_config(disable_thinking=False)
                try:
                    response = self._invoke(user_message, config, is_retry)
                except genai_errors.ClientError as exc2:
                    logger.error(
                        "Gemini API error (code=%s): %s",
                        getattr(exc2, "code", "unknown"),
                        getattr(exc2, "message", str(exc2)),
                    )
                    raise LLMServiceError(
                        f"Gemini API error ({getattr(exc2, 'code', 'unknown')}): "
                        f"{getattr(exc2, 'message', str(exc2))}"
                    ) from exc2
            else:
                logger.error(
                    "Gemini API error (code=%s): %s",
                    getattr(exc, "code", "unknown"),
                    getattr(exc, "message", str(exc)),
                )
                raise LLMServiceError(
                    f"Gemini API error ({getattr(exc, 'code', 'unknown')}): "
                    f"{getattr(exc, 'message', str(exc))}"
                ) from exc

        text = getattr(response, "text", None)
        if not text or not text.strip():
            logger.error("Gemini returned an empty response body.")
            raise LLMServiceError("Gemini returned an empty response.")

        usage = getattr(response, "usage_metadata", None)
        if usage is not None:
            logger.info(
                "Gemini token usage — prompt=%s, thinking=%s, output=%s, total=%s",
                getattr(usage, "prompt_token_count", "?"),
                getattr(usage, "thoughts_token_count", 0),
                getattr(usage, "candidates_token_count", "?"),
                getattr(usage, "total_token_count", "?"),
            )
            finish_reason = getattr(
                getattr(response, "candidates", [None])[0], "finish_reason", None
            )
            if finish_reason and str(finish_reason).upper().endswith("MAX_TOKENS"):
                logger.warning(
                    "Gemini response was cut off by max_output_tokens (%s). "
                    "Increase LLM_MAX_TOKENS in .env if this recurs.",
                    settings.LLM_MAX_TOKENS,
                )

        return text.strip()

    def _invoke(self, user_message: str, config: "types.GenerateContentConfig", is_retry: bool):
        try:
            logger.info(
                "Calling Gemini model=%s%s", settings.GEMINI_MODEL, " (retry)" if is_retry else ""
            )
            return self._client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=user_message,
                config=config,
            )
        except genai_errors.ClientError:
            raise  # handled by the caller (thinking_config fallback)
        except genai_errors.APIError as exc:
            # Covers ServerError (5xx: Gemini-side failure).
            logger.error(
                "Gemini API error (code=%s): %s",
                getattr(exc, "code", "unknown"),
                getattr(exc, "message", str(exc)),
            )
            raise LLMServiceError(
                f"Gemini API error ({getattr(exc, 'code', 'unknown')}): "
                f"{getattr(exc, 'message', str(exc))}"
            ) from exc
        except TimeoutError as exc:
            logger.error("Gemini request timed out: %s", exc)
            raise LLMServiceError(
                f"Gemini request timed out after {settings.GEMINI_TIMEOUT_SECONDS}s. "
                "Try again, or increase GEMINI_TIMEOUT_SECONDS in .env."
            ) from exc
        except Exception as exc:
            # Transport-level failures (connection errors, socket timeouts,
            # etc.) don't always surface as genai_errors.APIError - this is
            # the catch-all so nothing crashes the request unlogged.
            if "timeout" in type(exc).__name__.lower() or "timeout" in str(exc).lower():
                logger.error("Gemini request timed out: %s", exc)
                raise LLMServiceError(
                    f"Gemini request timed out after {settings.GEMINI_TIMEOUT_SECONDS}s. "
                    "Try again, or increase GEMINI_TIMEOUT_SECONDS in .env."
                ) from exc
            logger.error("Gemini call failed (%s): %s", type(exc).__name__, exc)
            raise LLMServiceError(f"Gemini call failed: {exc}") from exc

    @staticmethod
    def _strip_code_fences(text: str) -> str:
        """Removes ```json ... ``` or ``` ... ``` wrappers if Gemini adds
        them despite response_mime_type=application/json. This mirrors
        (but doesn't replace) the fence-stripping analysis_service.py
        already does before json.loads - defense in depth, not a
        duplicate responsibility, since analysis_service also handles
        stray characters before/after the fences."""
        stripped = text.strip()
        if stripped.startswith("```"):
            stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
            stripped = re.sub(r"\s*```$", "", stripped)
        return stripped.strip()

    @staticmethod
    def _is_valid_json(text: str) -> bool:
        try:
            json.loads(text)
            return True
        except (ValueError, json.JSONDecodeError):
            return False


llm_service = LLMService()
