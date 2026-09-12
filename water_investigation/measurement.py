"""Seeded instrument-level measurement model with primary-source provenance in docs/research/."""
from __future__ import annotations

from dataclasses import dataclass
from random import Random

from .ensemble import ScenarioSpec

# TE M3200: ±0.25% FSO. Net3 pressure readings are treated as psi and the
# modeled deployment uses a 100 psi full-scale transducer.
PRESSURE_FULL_SCALE_PSI = 100.0
PRESSURE_HALF_WIDTH_PSI = 0.0025 * PRESSURE_FULL_SCALE_PSI

# Hach Method 8021: 0.02–2.0 mg/L and ±0.05 mg/L (95% CI) at 1.00 mg/L.
FIELD_LOWER_RANGE_MG_L = 0.02
FIELD_UPPER_RANGE_MG_L = 2.0
FIELD_SIGMA_MG_L = 0.05 / 1.96

# Hach Method 10102: 0.03 mg/L sensitivity; same published 0.05 mg/L 95% CI
# width at its stated standard is used as an explicit normal approximation.
LAB_SENSITIVITY_MG_L = 0.03
LAB_SIGMA_MG_L = 0.05 / 1.96


@dataclass(frozen=True)
class Measurement:
    value: float
    channel: str
    model: str


def _rng(spec: ScenarioSpec, channel: str) -> Random:
    return Random(f"{spec.seed}:{channel}")


def pressure_delta(spec: ScenarioSpec, channel: str, true_delta_psi: float) -> Measurement:
    """Sample bounded instrument error; the ± accuracy limit is not treated as σ."""
    error = _rng(spec, channel).uniform(-PRESSURE_HALF_WIDTH_PSI, PRESSURE_HALF_WIDTH_PSI)
    return Measurement(true_delta_psi + error, channel, "TE M3200 ±0.25% FSO, uniform bounded-error assumption")


def chlorine(spec: ScenarioSpec, channel: str, true_mg_l: float, *, lab: bool) -> Measurement:
    sigma = LAB_SIGMA_MG_L if lab else FIELD_SIGMA_MG_L
    value = max(0.0, true_mg_l + _rng(spec, channel).gauss(0.0, sigma))
    method = "Hach Method 10102 normal approximation" if lab else "Hach Method 8021 normal approximation"
    return Measurement(value, channel, method)
