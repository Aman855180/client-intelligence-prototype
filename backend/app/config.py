"""
Central configuration for the Client Intelligence backend.

All values are read from environment variables so that no secrets
are hardcoded in source. A `.env` file can be used locally with
python-dotenv (already wired up in main.py).
"""

import os


class Settings:
    # --- LLM provider settings (Google Gemini) ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    # Note: Gemini model availability changes over time (e.g.
    # gemini-2.5-flash-lite has been retired for new users as of this
    # writing) - if this default 404s, check
    # https://ai.google.dev/gemini-api/docs/models for current model IDs.
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    # How long to wait for a single Gemini call before treating it as a
    # timeout. Kept generous since the transcript + strict JSON schema
    # instructions are a non-trivial generation task.
    GEMINI_TIMEOUT_SECONDS: int = int(os.getenv("GEMINI_TIMEOUT_SECONDS", "120"))
    # Kept generous: this schema is large, and some Gemini models spend
    # part of this budget on internal "thinking" tokens before writing
    # the JSON output (see llm_service._build_config). Too low a value
    # here is the most common cause of truncated/invalid JSON responses.
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "8192"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0"))

    # --- Retry / robustness settings ---
    # The LLM is asked to return strict JSON. If it fails to parse
    # or fails schema validation, we retry a bounded number of times
    # with a corrective follow-up instruction rather than silently
    # failing or fabricating a fallback response.
    MAX_LLM_RETRIES: int = int(os.getenv("MAX_LLM_RETRIES", "2"))

    # --- App settings ---
    APP_NAME: str = "FUME Client Intelligence API"
    APP_VERSION: str = "0.1.0"


settings = Settings()
