from water_investigation.web_demo import DemoHandler, run_investigation


def test_web_investigation_is_deterministic_and_uses_distinct_actions() -> None:
    first = run_investigation(7)
    assert first == run_investigation(7)
    assert len({step["selected"] for step in first["steps"]}) == 3
    assert abs(sum(first["steps"][-1]["posterior"].values()) - 1.0) < 1e-12


def test_web_server_allowlist_excludes_repository_internals() -> None:
    assert "/showcase/index.html" in DemoHandler.PUBLIC_PATHS
    assert "/.git/config" not in DemoHandler.PUBLIC_PATHS
