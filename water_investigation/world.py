"""Small seeded categorical world used only to exercise the orchestration loop."""
from __future__ import annotations

from dataclasses import dataclass, field
from random import Random

from .analytic import Action, Belief, posterior_after, score_action

HYPOTHESES = ("contamination", "leak", "sensor_fault")


def default_actions() -> tuple[Action, ...]:
    return (
        Action("field_chlorine_grab", 1.0, 1, {
            "contamination": {"detected": 0.80, "clear": 0.20},
            "leak": {"detected": 0.12, "clear": 0.88},
            "sensor_fault": {"detected": 0.08, "clear": 0.92},
        }),
        Action("lab_chlorine_assay", 5.0, 8, {
            "contamination": {"detected": 0.97, "clear": 0.03},
            "leak": {"detected": 0.03, "clear": 0.97},
            "sensor_fault": {"detected": 0.01, "clear": 0.99},
        }),
        Action("portable_pressure_reading", 3.0, 2, {
            "contamination": {"pressure_drop": 0.10, "normal": 0.90},
            "leak": {"pressure_drop": 0.85, "normal": 0.15},
            "sensor_fault": {"pressure_drop": 0.28, "normal": 0.72},
        }),
        Action("wait", 0.5, 1, {
            "contamination": {"anomaly_persists": 0.58, "settles": 0.42},
            "leak": {"anomaly_persists": 0.72, "settles": 0.28},
            "sensor_fault": {"anomaly_persists": 0.70, "settles": 0.30},
        }),
    )


@dataclass(frozen=True)
class Evidence:
    action: str
    outcome: str
    completed_at: int


@dataclass
class Episode:
    seed: int
    hidden_hypothesis: str
    belief: Belief = field(default_factory=lambda: {h: 1 / 3 for h in HYPOTHESES})
    budget: float = 10.0
    clock: int = 0
    pending: list[tuple[int, Action, str]] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)

    def choose(self, actions: tuple[Action, ...]) -> Action:
        affordable = [a for a in actions if a.cost <= self.budget]
        return max(affordable, key=lambda a: (score_action(self.belief, a), a.name))

    def schedule(self, action: Action, rng: Random) -> None:
        outcomes, probabilities = zip(*action.likelihood[self.hidden_hypothesis].items())
        outcome = rng.choices(outcomes, probabilities)[0]
        self.budget -= action.cost
        self.pending.append((self.clock + action.latency_steps, action, outcome))

    def advance(self) -> list[Evidence]:
        self.clock += 1
        due = [item for item in self.pending if item[0] <= self.clock]
        self.pending = [item for item in self.pending if item[0] > self.clock]
        emitted: list[Evidence] = []
        for completed_at, action, outcome in due:
            self.belief = posterior_after(self.belief, action, outcome)
            item = Evidence(action.name, outcome, completed_at)
            self.evidence.append(item)
            emitted.append(item)
        return emitted


def new_episode(seed: int) -> Episode:
    rng = Random(seed)
    return Episode(seed=seed, hidden_hypothesis=rng.choice(HYPOTHESES))

