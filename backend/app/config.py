"""Application settings loaded from environment variables / .env file."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────
    DATABASE_URL: str = ""

    # ── LLM — Groq (Primary) ─────────────────────────────────
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # ── LLM — OpenRouter (OpenAI-compatible) ────────────────
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "meta-llama/llama-3.3-70b-instruct"
    OPENROUTER_SITE_URL: str = "http://localhost:3000"
    OPENROUTER_SITE_NAME: str = "Polar Connect"

    # ── LLM — Gemini (Fallback) ──────────────────────────────
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash-lite"

    # ── Auth ──────────────────────────────────────────────────
    ADMIN_SECRET_KEY: str = "polar-connect-dev-secret-key-change-me"

    # ── Storage ───────────────────────────────────────────────
    UPLOAD_DIR: str = "./uploads"
    CHROMADB_DIR: str = "./chromadb_data"

    # ── CORS ──────────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # ── Default Admin (seed runner) ───────────────────────────
    ADMIN_EMAIL: str = "admin@ncpor.res.in"
    ADMIN_PASSWORD: str = "PolarConnect2026!"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
