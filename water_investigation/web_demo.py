"""Dependency-free local server for the shareable synthetic investigation demo."""
from __future__ import annotations

import argparse
import json
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
        "/showcase/index.html", "/showcase/styles.css", "/showcase/app.js",
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

    def do_GET(self) -> None:
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
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the local Water Investigation Agent experience.")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), DemoHandler)
    print(f"Water Investigation Agent: http://127.0.0.1:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
