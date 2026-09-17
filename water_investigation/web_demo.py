"""Dependency-free local server for the shareable synthetic investigation demo."""
from __future__ import annotations

import argparse
import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from random import Random

from .analytic import expected_information_gain, score_action
from .world import default_actions, new_episode

ROOT = Path(__file__).resolve().parents[1]


def run_investigation(seed: int) -> dict[str, object]:
    """Run the real analytic agent and expose truth only as post-run evaluation."""
    episode = new_episode(seed)
    available = list(default_actions())
    rng = Random(seed + 1)
    steps = []
    for _ in range(3):
        candidates = [action for action in available if action.cost <= episode.budget]
        scored = [{"action": action.name, "cost": action.cost,
                   "information_gain": expected_information_gain(episode.belief, action),
                   "score": score_action(episode.belief, action)} for action in candidates]
        selected = max(candidates, key=lambda action: (score_action(episode.belief, action), action.name))
        episode.schedule(selected, rng)
        available.remove(selected)
        evidence = []
        while not evidence:
            evidence = episode.advance()
        steps.append({"selected": selected.name, "candidates": scored,
                      "evidence": [item.outcome for item in evidence],
                      "posterior": dict(episode.belief), "remaining_budget": episode.budget})
    prediction = max(episode.belief, key=episode.belief.get)
    return {"seed": seed, "initial_belief": {name: 1 / 3 for name in episode.belief},
            "steps": steps, "prediction": prediction,
            "evaluation_truth": episode.hidden_hypothesis,
            "correct": prediction == episode.hidden_hypothesis,
            "scope": "Synthetic analytic correctness harness; not an operational result."}


class DemoHandler(SimpleHTTPRequestHandler):
    PUBLIC_PATHS = frozenset({
        "/showcase/index.html", "/showcase/styles.css", "/showcase/app.js", "/showcase/config.js",
        "/artifacts/net3-multiseed-benchmark.json",
        "/artifacts/sdwis-pwsid-06-public-report.json",
        "/artifacts/nors-drinking-water-public-report.json",
        "/docs/agent-architecture.md", "/docs/research/measurement-model-sources.md",
        "/docs/validation-protocol.md", "/docs/data-handling-security.md",
        "/docs/operational-readiness.md", "/PRIOR_ART_REPORT.md", "/FINDINGS.md",
        "/README.md",
    })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _cors_origin(self) -> str | None:
        allowed = os.environ.get("WATER_AGENT_ALLOWED_ORIGIN", "")
        request_origin = self.headers.get("Origin")
        if allowed == "*":
            return "*"
        if allowed and request_origin == allowed:
            return request_origin
        return None

    def _send_json(self, body: dict[str, object], status: int = 200) -> None:
        encoded = json.dumps(body).encode()
        self.send_response(status)
        origin = self._cors_origin()
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_OPTIONS(self) -> None:
        if self.path != "/api/investigate":
            self.send_error(404)
            return
        self.send_response(204)
        origin = self._cors_origin()
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json({"status": "ok", "service": "water-investigation-agent"})
            return
        if self.path == "/":
            self.path = "/showcase/index.html"
        if self.path not in self.PUBLIC_PATHS:
            self.send_error(404)
            return
        super().do_GET()

    def do_POST(self) -> None:
        if self.path != "/api/investigate":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(min(length, 1024)))
            seed = int(payload.get("seed", 7))
            if not 0 <= seed <= 999999:
                raise ValueError
            body = json.dumps(run_investigation(seed)).encode()
        except (ValueError, TypeError, json.JSONDecodeError):
            self.send_error(400, "seed must be an integer from 0 to 999999")
            return
        self._send_json(json.loads(body))


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the local Water Investigation Agent experience.")
    parser.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")))
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), DemoHandler)
    print(f"Water Investigation Agent: http://127.0.0.1:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nWater Investigation Agent stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
