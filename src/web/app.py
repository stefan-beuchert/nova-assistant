"""Flask app: the Nova web chat and health endpoint.

Server-rendered, no build step (docs/decisions.md D5). Conversation state lives
in process, keyed by a signed session cookie — there is no database (D4). The
`/chat` endpoint streams the agent loop's events to the browser as
newline-delimited JSON, read incrementally client-side via fetch().

Auth is deliberately not implemented here: in production the app is reached only
through Caddy + Authentik forward_auth on the tailnet (docs/platform-assumptions.md).
"""

import json
import logging
import uuid

from flask import Flask, Response, jsonify, render_template, request, session

from src.agent.loop import build_client, run_turn
from src.agent.tools import build_registry
from src.config import Config

# session id -> message history. In-memory only; cleared on restart (stateless PoC).
_CONVERSATIONS: dict[str, list] = {}


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = Config.SECRET_KEY

    # Built once; None when no API key is configured so /health still works.
    client = build_client(Config.ANTHROPIC_API_KEY) if Config.ANTHROPIC_API_KEY else None
    # The mounted tool set (built-ins + allowlisted MCP sources). Discovery is
    # best-effort, so an unreachable source just yields no tools.
    registry = build_registry(Config)

    @app.get("/health")
    def health():
        return jsonify(
            status="ok",
            model=Config.ANTHROPIC_MODEL,
            ready=client is not None,
            sources=registry.mounted_sources,
        )

    @app.get("/version")
    def version():
        return jsonify(version=Config.APP_VERSION, build_time=Config.APP_BUILD_TIME)

    @app.get("/")
    def index():
        return render_template(
            "index.html", models=Config.MODELS, default_model=Config.ANTHROPIC_MODEL
        )

    @app.post("/chat")
    def chat():
        if client is None:
            return jsonify(error="ANTHROPIC_API_KEY is not configured"), 503

        data = request.get_json(silent=True) or {}
        message = (data.get("message") or "").strip()
        if not message:
            return jsonify(error="empty message"), 400

        # The switcher picks which Claude reasons this turn. Validate against the
        # config allowlist (Config.MODELS); anything else falls back to the default
        # — the UI can never ask for a model that isn't configured.
        model = data.get("model")
        if model not in Config.MODEL_IDS:
            model = Config.ANTHROPIC_MODEL

        sid = session.get("sid")
        if not sid:
            sid = uuid.uuid4().hex
            session["sid"] = sid

        messages = _CONVERSATIONS.setdefault(sid, [])
        messages.append({"role": "user", "content": message})

        def generate():
            try:
                for event in run_turn(
                    client, model, Config.MAX_TOKENS, messages, registry
                ):
                    yield json.dumps(event) + "\n"
            except Exception as exc:  # don't leak a stack trace to the browser
                app.logger.exception("agent turn failed")
                yield json.dumps({"type": "error", "message": str(exc)}) + "\n"

        return Response(generate(), mimetype="application/x-ndjson")

    @app.post("/reset")
    def reset():
        sid = session.get("sid")
        if sid:
            _CONVERSATIONS.pop(sid, None)
        return jsonify(status="ok")

    return app


app = create_app()


if __name__ == "__main__":
    logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO))
    # threaded=True so a streaming /chat response doesn't block other requests.
    app.run(host=Config.HOST, port=Config.PORT, threaded=True)
