.PHONY: test verify demo

test:
	.venv/bin/python -m pytest -q

verify:
	.venv/bin/python -m water_investigation.verify_artifacts

demo:
	.venv/bin/python -m water_investigation.synthetic_pilot --telemetry docs/examples/historian-replay.csv --channel-map docs/examples/historian-channel-map.json --required-channel pressure_delta_psi --required-channel quality_delta_mg_l
