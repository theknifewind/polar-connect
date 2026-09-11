"""Unified LLM provider router — Groq (primary) → Gemini (fallback).

Single interface: ``await generate(system_prompt, user_prompt, temperature)``
"""

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
_GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


async def generate(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
) -> str:
    """Call the LLM with OpenRouter, Groq, then Gemini fallback."""

    # OpenRouter keys are sometimes pasted into the old Groq setting. Support
    # that existing setup while allowing the provider to be configured clearly.
    openrouter_key = settings.OPENROUTER_API_KEY
    if not openrouter_key and settings.GROQ_API_KEY.startswith("sk-or-"):
        openrouter_key = settings.GROQ_API_KEY

    if openrouter_key:
        try:
            result = await _call_openrouter(
                openrouter_key, system_prompt, user_prompt, temperature
            )
            if result:
                return result
        except Exception as exc:
            logger.warning("OpenRouter API failed, falling back to Groq: %s", exc)

    # ── Primary: Groq (OpenAI-compatible) ────────────────────
    if settings.GROQ_API_KEY:
        try:
            result = await _call_groq(system_prompt, user_prompt, temperature)
            if result:
                return result
        except Exception as exc:
            logger.warning("Groq API failed, falling back to Gemini: %s", exc)

    # ── Fallback: Google Gemini ──────────────────────────────
    if settings.GEMINI_API_KEY:
        try:
            result = await _call_gemini(system_prompt, user_prompt, temperature)
            if result:
                return result
        except Exception as exc:
            logger.warning("Gemini API also failed: %s", exc)

    raise RuntimeError(
        "No LLM provider available. Set OPENROUTER_API_KEY, GROQ_API_KEY, "
        "or GEMINI_API_KEY in .env"
    )


# ─────────────────────────────────────────────────────────────
# Provider implementations
# ─────────────────────────────────────────────────────────────

async def _call_openrouter(
    api_key: str, system_prompt: str, user_prompt: str, temperature: float
) -> str:
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            _OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": settings.OPENROUTER_SITE_URL,
                "X-Title": settings.OPENROUTER_SITE_NAME,
            },
            json={
                "model": settings.OPENROUTER_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": temperature,
                "max_tokens": 4096,
            },
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

async def _call_groq(
    system_prompt: str, user_prompt: str, temperature: float
) -> str:
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            _GROQ_URL,
            headers={
                "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": temperature,
                "max_tokens": 4096,
            },
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def _call_gemini(
    system_prompt: str, user_prompt: str, temperature: float
) -> str:
    url = _GEMINI_URL.format(model=settings.GEMINI_MODEL)
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            url,
            params={"key": settings.GEMINI_API_KEY},
            headers={"Content-Type": "application/json"},
            json={
                "system_instruction": {"parts": [{"text": system_prompt}]},
                "contents": [{"parts": [{"text": user_prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": 4096,
                },
            },
        )
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
