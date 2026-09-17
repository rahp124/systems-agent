"""Small WSGI adapter for PythonAnywhere and other WSGI hosts."""
from __future__ import annotations

import json
import os
from typing import Iterable

from .web_demo import run_investigation


def _response(start_response, status: str, body: bytes, content_type: str = "application/json", headers: list[tuple[str, str]] | None = None):
    response_headers = [("Content-Type", content_type), ("Content-Length", str(len(body)))]
    response_headers.extend(headers or [])
    start_response(status, response_headers)
    return [body]


def application(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET").upper()
    allowed_origin = os.environ.get("WATER_AGENT_ALLOWED_ORIGIN", "")
    request_origin = environ.get("HTTP_ORIGIN", "")
    cors = []
    if allowed_origin == "*" or (allowed_origin and request_origin == allowed_origin):
        cors = [("Access-Control-Allow-Origin", request_origin if allowed_origin != "*" else "*"), ("Vary", "Origin")]

    if path == "/health" and method == "GET":
        return _response(start_response, "200 OK", b'{"status":"ok","service":"water-investigation-agent"}', headers=cors)
    if path == "/api/investigate" and method == "OPTIONS":
        return _response(start_response, "204 No Content", b"", headers=cors + [("Access-Control-Allow-Methods", "POST, OPTIONS"), ("Access-Control-Allow-Headers", "Content-Type")])
    if path == "/api/investigate" and method == "POST":
        try:
            length = min(int(environ.get("CONTENT_LENGTH", "0") or "0"), 1024)
            payload = json.loads(environ["wsgi.input"].read(length))
            seed = int(payload.get("seed", 7))
            if not 0 <= seed <= 999999:
                raise ValueError
        except (ValueError, TypeError, json.JSONDecodeError):
            return _response(start_response, "400 Bad Request", b'{"error":"seed must be an integer from 0 to 999999"}', headers=cors)
        return _response(start_response, "200 OK", json.dumps(run_investigation(seed)).encode(), headers=cors)
    return _response(start_response, "404 Not Found", b'{"error":"not found"}', headers=cors)
