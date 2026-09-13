from __future__ import annotations

import argparse
from random import Random

from .analytic import expected_information_gain, score_action
from .world import default_actions, new_episode


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the sequential-investigation oracle.")
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    episode = new_episode(args.seed)
    actions = default_actions()
    rng = Random(args.seed + 1)
    print(f"seed={args.seed}; hidden ground truth remains evaluator-only")
    for _ in range(3):
        candidates = [a for a in actions if a.cost <= episode.budget]
        for action in candidates:
            print(f"t={episode.clock} candidate={action.name} eig={expected_information_gain(episode.belief, action):.3f} score={score_action(episode.belief, action):.3f}")
        selected = episode.choose(actions)
        episode.schedule(selected, rng)
        print(f"t={episode.clock} selected={selected.name}; pending_until={episode.clock + selected.latency_steps}")
        evidence_count = len(episode.evidence)
        while len(episode.evidence) == evidence_count:
            for evidence in episode.advance():
                print(f"t={evidence.completed_at} evidence={evidence.action}:{evidence.outcome}; posterior={episode.belief}")


if __name__ == "__main__":
    main()
