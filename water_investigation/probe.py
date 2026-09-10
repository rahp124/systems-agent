"""Real EPyT-Flow feasibility probe. Writes measurements; it never fabricates a likelihood."""
from __future__ import annotations

import argparse
import json
import time
import traceback
from pathlib import Path

import numpy as np
from epanet_plus import EpanetConstants
from epyt_flow.data.networks import load_ltown, load_net3
from epyt_flow.simulation import ScenarioSimulator
from epyt_flow.simulation.events import AbruptLeakage


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "networks"
ARTIFACTS = ROOT / "artifacts"


def _configure(simulator: ScenarioSimulator) -> tuple[list[str], list[str]]:
    nodes = simulator.epanet_api.get_all_nodes_id()
    links = simulator.epanet_api.get_all_links_id()
    simulator.set_pressure_sensors(nodes[:4])
    simulator.set_flow_sensors(links[:1])
    simulator.set_node_quality_sensors([nodes[0], nodes[4]])
    # Preserve each bundled network's compatible hydraulic/quality cadence. EPyT
    # validates these settings eagerly, so changing the pair is not atomic.
    simulator.set_general_parameters(
        simulation_duration=48 * 60 * 60,
        flow_units_id=EpanetConstants.EN_CFS,
    )
    return nodes, links


def _simulate(kind: str, network: str) -> dict[str, object]:
    config = load_net3(download_dir=str(CACHE), verbose=False) if network == "net3" else load_ltown(download_dir=str(CACHE), verbose=False)
    started = time.perf_counter()
    with ScenarioSimulator(scenario_config=config, raise_exception_on_error=True) as simulator:
        nodes, links = _configure(simulator)
        # Net3 begins with reservoirs/tanks and pump links. Use ordinary junction/pipe candidates
        # rather than assuming the first IDs accept a leakage or chemical source.
        event_node = nodes[4]
        if kind == "leak":
            simulator.add_leakage(AbruptLeakage(link_id=None, node_id=event_node, diameter=0.005, start_time=4 * 3600, end_time=48 * 3600))
        elif kind == "contamination":
            simulator.enable_chemical_analysis("spike")
            simulator.add_quality_source(
                node_id=event_node, source_type=EpanetConstants.EN_MASS,
                pattern=np.array([0.0] * 16 + [1.0] * 8 + [0.0] * 168), source_strength=1.0,
            )
        elif kind == "sensor_fault":
            # This class is deliberately post-processing: the unmodified hydraulic trace is retained.
            sensor_fault_shift = 5.0
        else:
            raise ValueError(f"Unknown event class: {kind}")
        data = simulator.run_simulation(frozen_sensor_config=True)
        pressures = data.get_data_pressures()
        flows = data.get_data_flows()
        quality = data.get_data_nodes_quality()
        if kind == "sensor_fault":
            pressures = pressures.copy()
            pressures[16:, 0] += sensor_fault_shift
    return {
        "event_class": kind,
        "runtime_seconds": round(time.perf_counter() - started, 3),
        "pressure_shape": list(pressures.shape),
        "flow_shape": list(flows.shape),
        "quality_shape": list(quality.shape),
        "pressure_mean": float(np.mean(pressures)),
        "flow_mean": float(np.mean(flows)),
        "quality_max": float(np.max(quality)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe EPyT-Flow scenario feasibility.")
    parser.add_argument("--network", choices=("net3", "ltown"), default="net3")
    parser.add_argument("--classes", nargs="+", choices=("contamination", "leak", "sensor_fault"), default=("contamination", "leak", "sensor_fault"))
    args = parser.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    ARTIFACTS.mkdir(exist_ok=True)
    findings: dict[str, object] = {"network": args.network, "results": [], "failures": []}
    for event_class in args.classes:
        try:
            findings["results"].append(_simulate(event_class, args.network))
        except Exception as error:  # Findings must preserve simulator/API failures.
            findings["failures"].append({"event_class": event_class, "error": repr(error), "traceback": traceback.format_exc()})
    destination = ARTIFACTS / f"{args.network}-probe.json"
    destination.write_text(json.dumps(findings, indent=2) + "\n")
    print(destination)
    print(json.dumps(findings, indent=2))


if __name__ == "__main__":
    main()
