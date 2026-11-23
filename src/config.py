"""Configuration, all from environment variables (twelve-factor).

Nothing here is hardcoded except safe defaults. Secrets come from `.env`
(gitignored) via python-dotenv in local development, or the container
environment in deployment.
"""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # Cloud reasoning model
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")
    MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "16000"))

    # Web server
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "8080"))
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "info")
    APP_URL = os.environ.get("APP_URL", "")
    # Ephemeral per-boot key if unset — acceptable for the single-user PoC.
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(32).hex()

    # Phase 3, not wired yet: Constellation's read-only MCP server.
    CONSTELLATION_MCP_URL = os.environ.get("CONSTELLATION_MCP_URL", "")
