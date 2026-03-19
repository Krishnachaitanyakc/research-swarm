"""Tests for Pareto integration."""

import pytest
from autoresearch_swarm.pareto_integration import (
    is_dominated,
    compute_pareto_frontier,
    MultiObjectiveTracker,
)


def test_is_dominated_true():
    assert is_dominated([1, 1], [2, 2]) is True


def test_is_dominated_false():
    assert is_dominated([2, 1], [1, 2]) is False


def test_is_dominated_equal():
    assert is_dominated([1, 1], [1, 1]) is False


def test_is_dominated_partial():
    assert is_dominated([1, 2], [2, 2]) is True


def test_compute_pareto_frontier_basic():
    results = [
        {"accuracy": 0.9, "speed": 0.5},
        {"accuracy": 0.8, "speed": 0.9},
        {"accuracy": 0.7, "speed": 0.4},  # dominated
    ]
    frontier = compute_pareto_frontier(results, ["accuracy", "speed"])
    assert len(frontier) == 2
    assert results[2] not in frontier


def test_compute_pareto_frontier_empty():
    assert compute_pareto_frontier([], ["accuracy"]) == []


def test_compute_pareto_frontier_single():
    results = [{"accuracy": 0.9}]
    frontier = compute_pareto_frontier(results, ["accuracy"])
    assert len(frontier) == 1


def test_multi_objective_tracker():
    tracker = MultiObjectiveTracker(metric_keys=["accuracy", "speed"])
    tracker.record("agent-1", {"accuracy": 0.9, "speed": 0.5}, {"lr": 0.001})
    tracker.record("agent-2", {"accuracy": 0.8, "speed": 0.9}, {"lr": 0.002})
    tracker.record("agent-3", {"accuracy": 0.7, "speed": 0.4}, {"lr": 0.003})
    frontier = tracker.get_frontier()
    assert len(frontier) == 2


def test_should_merge_on_frontier():
    tracker = MultiObjectiveTracker(metric_keys=["accuracy", "speed"])
    tracker.record("agent-1", {"accuracy": 0.9, "speed": 0.5}, {"lr": 0.001})
    candidate = {"accuracy": 0.8, "speed": 0.95, "agent_id": "agent-2", "params": {}}
    assert tracker.should_merge(candidate) is True


def test_should_merge_dominated():
    tracker = MultiObjectiveTracker(metric_keys=["accuracy", "speed"])
    tracker.record("agent-1", {"accuracy": 0.9, "speed": 0.9}, {"lr": 0.001})
    candidate = {"accuracy": 0.5, "speed": 0.5, "agent_id": "agent-2", "params": {}}
    assert tracker.should_merge(candidate) is False
