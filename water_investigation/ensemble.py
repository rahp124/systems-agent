"""Build a small, seeded Net3 trace ensemble for the first evaluation slice."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from random import Random

import numpy as np
from epanet_plus import EpanetConstants
from epyt_flow.data.networks import load_net3
from epyt_flow.simulation import ScenarioSimulator
from epyt_flow.simulation.events import AbruptLeakage

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "artifacts" / "net3-ensemble.npz"
CACHE = ROOT / ".cache" / "networks"
HYPOTHESES = ("contamination", "leak", "sensor_fault")
ENSEMBLE_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class ScenarioSpec:
    scenario_id: str
    event_class: str
    seed: int
    event_start_seconds: int
    magnitude: float


def scenario_specs(per_class: int, seed: int) -> list[ScenarioSpec]:
    """Produce stable scenario parameters without exposing them to an evaluator."""
    rng = Random(seed)
    specs: list[ScenarioSpec] = []
    for event_class in HYPOTHESES:
        for index in range(per_class):
            event_seed = rng.randrange(2**31)
            event_rng = Random(event_seed)
            specs.append(ScenarioSpec(
                scenario_id=f"{event_class}-{index:03d}", event_class=event_class,
                seed=event_seed, event_start_seconds=event_rng.choice((4, 6, 8, 10)) * 3600,
                magnitude=event_rng.uniform(0.25, 1.0),
            ))
    return specs


def _configure(simulator: ScenarioSimulator) -> tuple[list[str], list[str]]:
    nodes = simulator.epanet_api.get_all_nodes_id()
    links = simulator.epanet_api.get_all_links_id()
    simulator.set_pressure_sensors(nodes[:4])
    simulator.set_flow_sensors(links[:1])
    simulator.set_node_quality_sensors([nodes[0], nodes[4]])
    simulator.set_general_parameters(simulation_duration=48 * 60 * 60, flow_units_id=EpanetConstants.EN_CFS)
    return nodes, links


def simulate(spec: ScenarioSpec) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return normalized trace arrays for one hidden scenario configuration."""
    config = load_net3(download_dir=str(CACHE), verbose=False)
    with ScenarioSimulator(scenario_config=config, raise_exception_on_error=True) as simulator:
        nodes, _ = _configure(simulator)
        event_node = nodes[4]
        # Every scenario uses the same chemical-quality channel. Without this,
        # non-contamination traces contain water age and are not comparable to
        # contamination concentration traces.
        simulator.enable_chemical_analysis("spike")
        if spec.event_class == "contamination":
            start_step = spec.event_start_seconds // 3600
            pattern = np.array([0.0] * start_step + [1.0] * 2 + [0.0] * (49 - start_step - 2))
            simulator.add_quality_source(event_node, EpanetConstants.EN_MASS, pattern=pattern,
                                         # Scale the injected mass so observable concentrations
                                         # occupy the cited 0.02–2.0 mg/L field-method range.
                                         source_strength=100.0 * spec.magnitude)
        elif spec.event_class == "leak":
            simulator.add_leakage(AbruptLeakage(link_id=None, node_id=event_node,
                                                 diameter=0.002 + spec.magnitude * 0.006,
                                                 start_time=spec.event_start_seconds,
                                                 end_time=48 * 3600))
        elif spec.event_class not in {"sensor_fault", "baseline"}:
            raise ValueError(f"unknown event class: {spec.event_class}")
        data = simulator.run_simulation(frozen_sensor_config=True)
        pressure = data.get_data_pressures().astype(np.float64)
        flow = data.get_data_flows().astype(np.float64)
        quality = data.get_data_nodes_quality().astype(np.float64)
        if spec.event_class == "sensor_fault":
            start_index = spec.event_start_seconds // 3600
            pressure[start_index:, 0] += 1.0 + spec.magnitude * 4.0
        return pressure, flow, quality


def build_ensemble(per_class: int = 40, seed: int = 20260911, output: Path = DEFAULT_OUTPUT) -> Path:
    if per_class < 2:
        raise ValueError("per_class must be at least two")
    CACHE.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    specs = scenario_specs(per_class, seed)
    baseline = simulate(ScenarioSpec("baseline", "baseline", seed, 0, 0.0))
    traces = [simulate(spec) for spec in specs]
    np.savez_compressed(
        output,
        metadata=np.array(json.dumps({"schema_version": ENSEMBLE_SCHEMA_VERSION,
                                      "network": "net3", "seed": seed,
                                      "scenarios": [asdict(spec) for spec in specs]})),
        pressure=np.stack([trace[0] for trace in traces]),
        flow=np.stack([trace[1] for trace in traces]),
        quality=np.stack([trace[2] for trace in traces]),
        baseline_pressure=baseline[0],
        baseline_flow=baseline[1],
        baseline_quality=baseline[2],
    )
    return output


def load_ensemble(path: Path = DEFAULT_OUTPUT) -> tuple[list[ScenarioSpec], np.ndarray, np.ndarray, np.ndarray, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    with np.load(path, allow_pickle=False) as archive:
        metadata = json.loads(str(archive["metadata"]))
        specs = [ScenarioSpec(**item) for item in metadata["scenarios"]]
        return (specs, archive["pressure"], archive["flow"], archive["quality"],
                (archive["baseline_pressure"], archive["baseline_flow"], archive["baseline_quality"]))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a seeded Net3 trace ensemble.")
    parser.add_argument("--per-class", type=int, default=40)
    parser.add_argument("--seed", type=int, default=20260911)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(build_ensemble(args.per_class, args.seed, args.output))


if __name__ == "__main__":
    main()
