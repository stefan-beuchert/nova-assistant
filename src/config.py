"""Configuration, all from environment variables (twelve-factor).

Nothing here is hardcoded except safe defaults. Secrets come from `.env`
(gitignored) via python-dotenv in local development, or the container
environment in deployment.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# The set of Claude models offered in the UI's model switcher. Kept in config —
# the same posture as the tool allowlist (D3): what the user can pick is *data in
# config*, never something the UI or user input can invent. A model choice only
# changes which Claude reasons; it never widens what data Nova can reach (that is
# the tool allowlist, ADR-0009 / D3). This is a choice *within* the accepted
# cloud-Claude decision, not a multi-provider abstraction (D1, PROJECT.md §3).
# Override with ANTHROPIC_MODELS as a comma-separated "id=Label,id=Label" list.
_DEFAULT_MODELS = (
    "claude-opus-4-8=Opus 4.8,"
    "claude-sonnet-5=Sonnet 5,"
    "claude-haiku-4-5-20251001=Haiku 4.5"
)


def _parse_models(raw: str) -> list[dict]:
    """Parse "id=Label,id=Label" into [{"id", "label"}]. A bare id uses its id
    as the label; blank/malformed entries are skipped."""
    models = []
    for item in raw.split(","):
        model_id, _, label = item.partition("=")
        model_id, label = model_id.strip(), label.strip()
        if model_id:
            models.append({"id": model_id, "label": label or model_id})
    return models


class Config:
    # Cloud reasoning model
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")
    MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "16000"))

    # Selectable models (switcher). Guarantee the active default is always offered.
    MODELS = _parse_models(os.environ.get("ANTHROPIC_MODELS", _DEFAULT_MODELS))
    if ANTHROPIC_MODEL not in {m["id"] for m in MODELS}:
        MODELS = [{"id": ANTHROPIC_MODEL, "label": ANTHROPIC_MODEL}, *MODELS]
    # Allowlist for validating a requested model server-side — the UI cannot ask
    # for a model that isn't configured here.
    MODEL_IDS = frozenset(m["id"] for m in MODELS)

    # Web server
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "8080"))
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "info")
    APP_URL = os.environ.get("APP_URL", "")
    # Ephemeral per-boot key if unset — acceptable for the single-user PoC.
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(32).hex()

    # Allowlisted read-only MCP sources (ADR-0009 / D3). Each is off unless its URL
    # is configured; adding one here is a deliberate CLAUDE.md §2 decision. Vitae
    # (medical) and photos are permanently absent and must never be added.
    CONSTELLATION_MCP_URL = os.environ.get("CONSTELLATION_MCP_URL", "")
    # Nexus's read-only calendar MCP server (2nd source, added 2026-11-25 with
    # explicit user confirmation; ADR-0009 amendment owned upstream by the Architect).
    NEXUS_MCP_URL = os.environ.get("NEXUS_MCP_URL", "")

    # Running-version stamp, set by deploy/deploy.sh via compose; surfaced at /version.
    APP_VERSION = os.environ.get("APP_VERSION", "dev")
    APP_BUILD_TIME = os.environ.get("APP_BUILD_TIME", "")
