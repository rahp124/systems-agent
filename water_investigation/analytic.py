"""Exact categorical Bayes and EIG calculations used as the spike's oracle."""
from __future__ import annotations

from dataclasses import dataclass
from math import log2
from typing import Mapping

Belief = dict[str, float]


@dataclass(frozen=True)
class Action:
    name: str
    cost: float
    latency_steps: int
    # likelihood[hypothesis][outcome] = P(outcome | hypothesis, action)
    likelihood: Mapping[str, Mapping[str, float]]


def _normalized(values: Mapping[str, float]) -> Belief:
    total = sum(values.values())
    if total <= 0:
        raise ValueError("probabilities must have positive mass")
    return {key: value / total for key, value in values.items()}


def update_belief(prior: Mapping[str, float], likelihood: Mapping[str, float]) -> Belief:
    """Return P(H | observation) from a hypothesis-indexed likelihood vector."""
    if set(prior) != set(likelihood):
        raise ValueError("prior and likelihood must name the same hypotheses")
    if any(value < 0 for value in likelihood.values()):
        raise ValueError("likelihood values cannot be negative")
    return _normalized({hypothesis: prior[hypothesis] * likelihood[hypothesis] for hypothesis in prior})


def entropy(belief: Mapping[str, float]) -> float:
    return -sum(probability * log2(probability) for probability in belief.values() if probability > 0)


def outcome_probability(belief: Mapping[str, float], action: Action, outcome: str) -> float:
    return sum(belief[hypothesis] * action.likelihood[hypothesis].get(outcome, 0.0) for hypothesis in belief)


def posterior_after(belief: Mapping[str, float], action: Action, outcome: str) -> Belief:
    return update_belief(belief, {h: action.likelihood[h].get(outcome, 0.0) for h in belief})


def expected_information_gain(belief: Mapping[str, float], action: Action) -> float:
    outcomes = set().union(*(distribution.keys() for distribution in action.likelihood.values()))
    expected_entropy = sum(
        outcome_probability(belief, action, outcome) * entropy(posterior_after(belief, action, outcome))
        for outcome in outcomes
        if outcome_probability(belief, action, outcome) > 0
    )
    return entropy(belief) - expected_entropy


def score_action(belief: Mapping[str, float], action: Action, latency_penalty: float = 0.25) -> float:
    denominator = action.cost + latency_penalty * action.latency_steps
    if denominator <= 0:
        raise ValueError("expected action cost must be positive")
    return expected_information_gain(belief, action) / denominator

