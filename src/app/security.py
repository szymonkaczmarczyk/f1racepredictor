from __future__ import annotations

import base64
import hashlib
import os
import re
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

TRUSTED_HOSTS = [
    h.strip() for h in os.environ.get("F1_TRUSTED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()
]
MAX_BODY_BYTES = 64 * 1024
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def install(app: Flask) -> None:
    app.config["TRUSTED_HOSTS"] = TRUSTED_HOSTS
    app.config["MAX_CONTENT_LENGTH"] = MAX_BODY_BYTES
    policy = _content_security_policy(Path(app.root_path) / "templates")

    @app.before_request
    def _same_origin_only():
        if request.method in SAFE_METHODS:
            return None
        site = request.headers.get("Sec-Fetch-Site")
        if site and site not in ("same-origin", "none"):
            return jsonify({"error": "cross-site request blocked"}), 403
        origin = request.headers.get("Origin")
        if origin and urlparse(origin).netloc != request.host:
            return jsonify({"error": "cross-origin request blocked"}), 403
        return None

    @app.after_request
    def _headers(response):
        headers = response.headers
        headers["Content-Security-Policy"] = policy
        headers["X-Content-Type-Options"] = "nosniff"
        headers["X-Frame-Options"] = "DENY"
        headers["Referrer-Policy"] = "no-referrer"
        headers["Cross-Origin-Opener-Policy"] = "same-origin"
        headers["Cross-Origin-Resource-Policy"] = "same-origin"
        headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if request.path.startswith("/api/"):
            headers["Cache-Control"] = "no-store"
        return response

    @app.errorhandler(HTTPException)
    def _http_error(exc: HTTPException):
        if request.path.startswith("/api/"):
            return jsonify({"error": exc.description or exc.name}), exc.code
        return exc

    @app.errorhandler(Exception)
    def _unhandled(exc: Exception):
        app.logger.exception("unhandled error on %s", request.path)
        return jsonify({"error": "internal error"}), 500


def _content_security_policy(templates: Path) -> str:
    bodies = {
        body
        for template in sorted(templates.rglob("*.html"))
        for body in re.findall(r"<script>(.*?)</script>", template.read_text(encoding="utf-8"), re.S)
    }
    hashes = " ".join(
        "'sha256-" + base64.b64encode(hashlib.sha256(body.encode("utf-8")).digest()).decode() + "'"
        for body in sorted(bodies)
    )
    return (
        "default-src 'self'; "
        f"script-src 'self' {hashes}; "
        "style-src 'self' 'unsafe-inline'; "
        "font-src 'self'; "
        "img-src 'self' data: blob:; "
        "connect-src 'self'; "
        "object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
    )
