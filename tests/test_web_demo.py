from pathlib import Path
from urllib.parse import urlsplit

from water_investigation.web_demo import DemoHandler, run_investigation
from water_investigation.wsgi import application


def test_wsgi_health_endpoint() -> None:
    captured = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = headers

    body = b"".join(application({"PATH_INFO": "/health", "REQUEST_METHOD": "GET"}, start_response))
    assert captured["status"] == "200 OK"
    assert b'"status":"ok"' in body


def test_web_investigation_is_deterministic_and_uses_distinct_actions() -> None:
    first = run_investigation(7)
    assert first == run_investigation(7)
    assert len({step["selected"] for step in first["steps"]}) == 3
    assert abs(sum(first["steps"][-1]["posterior"].values()) - 1.0) < 1e-12


def test_web_server_allowlist_excludes_repository_internals() -> None:
    assert "/showcase/index.html" in DemoHandler.PUBLIC_PATHS
    assert "/showcase/config.js" in DemoHandler.PUBLIC_PATHS
    assert "/docs/utility-pilot-brief.md" in DemoHandler.PUBLIC_PATHS
    assert "/.git/config" not in DemoHandler.PUBLIC_PATHS
    assert DemoHandler.ASSET_ALIASES["/styles.css"] == "/showcase/styles.css"
    assert urlsplit("/styles.css?v=20260918-2").path in DemoHandler.ASSET_ALIASES


def test_showcase_leads_with_guidance_and_keeps_the_real_agent_runnable() -> None:
    page = (Path(__file__).parents[1] / "showcase" / "index.html").read_text()
    script = (Path(__file__).parents[1] / "showcase" / "app.js").read_text()
    assert "When water-system signals conflict, decide what to measure next." in page
    assert "Run investigation" in page
    assert "What it means" in page
    assert "Review returned evidence" not in page
    assert "resultStory.setAttribute('aria-labelledby','step-title')" in script
    assert "matchMedia('(max-width: 900px)')" in script
