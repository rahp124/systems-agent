from math import isclose
from random import Random

from water_investigation.analytic import Action, entropy, expected_information_gain, posterior_after, update_belief
from water_investigation.world import default_actions, new_episode


def test_bayes_update_matches_hand_calculation() -> None:
    posterior = update_belief({"a": 0.5, "b": 0.5}, {"a": 0.8, "b": 0.2})
    assert posterior == {"a": 0.8, "b": 0.2}


def test_perfect_test_has_one_bit_of_information_for_uniform_binary_belief() -> None:
    action = Action("perfect", 1, 0, {"a": {"yes": 1}, "b": {"no": 1}})
    assert isclose(expected_information_gain({"a": 0.5, "b": 0.5}, action), 1.0)


def test_uninformative_test_has_zero_information_gain() -> None:
    action = Action("none", 1, 0, {"a": {"yes": 0.5, "no": 0.5}, "b": {"yes": 0.5, "no": 0.5}})
    assert isclose(expected_information_gain({"a": 0.5, "b": 0.5}, action), 0.0)


def test_posterior_is_normalized_after_an_outcome() -> None:
    posterior = posterior_after({"a": 0.4, "b": 0.6}, Action("x", 1, 0, {"a": {"yes": .9}, "b": {"yes": .2}}), "yes")
    assert isclose(sum(posterior.values()), 1.0)
    assert posterior["a"] > posterior["b"]


def test_seeded_episode_replays_identically() -> None:
    left, right = new_episode(11), new_episode(11)
    actions = default_actions()
    for episode in (left, right):
        action = episode.choose(actions)
        episode.schedule(action, Random(12))
        while episode.pending:
            episode.advance()
    assert left.hidden_hypothesis == right.hidden_hypothesis
    assert left.evidence == right.evidence
    assert left.belief == right.belief


def test_entropy_of_certainty_is_zero() -> None:
    assert entropy({"a": 1.0, "b": 0.0}) == 0.0
