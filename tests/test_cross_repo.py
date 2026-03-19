"""Tests for cross-repo coordination."""

import pytest
from research_swarm.config import SwarmConfig
from research_swarm.cross_repo import CrossRepoCoordinator


def test_cross_repo_creation():
    config = SwarmConfig(num_agents=2)
    cross = CrossRepoCoordinator(repo_paths=["/tmp/repo1", "/tmp/repo2"], config=config)
    assert len(cross.coordinators) == 2


def test_assign_all_roles():
    config = SwarmConfig(num_agents=2)
    cross = CrossRepoCoordinator(repo_paths=["/tmp/repo1", "/tmp/repo2"], config=config)
    result = cross.assign_all_roles()
    assert "/tmp/repo1" in result
    assert "/tmp/repo2" in result
    assert len(result["/tmp/repo1"]) == 2
    assert len(result["/tmp/repo2"]) == 2


def test_collect_all_results():
    config = SwarmConfig(num_agents=1, roles_distribution={"explorer": 1.0})
    cross = CrossRepoCoordinator(repo_paths=["/tmp/repo1", "/tmp/repo2"], config=config)
    cross.assign_all_roles()
    # Run experiments
    for coord in cross.coordinators:
        for agent in coord.agents:
            agent.run_experiment({"lr": 0.001})
    results = cross.collect_all_results()
    assert len(results) == 2
    assert all("repo_path" in r for r in results)


def test_global_best():
    config = SwarmConfig(num_agents=1, roles_distribution={"explorer": 1.0})
    cross = CrossRepoCoordinator(repo_paths=["/tmp/repo1", "/tmp/repo2"], config=config)
    cross.assign_all_roles()
    # Manually set metrics
    cross.coordinators[0].agents[0].report_result(0.8, {"lr": 0.001})
    cross.coordinators[1].agents[0].report_result(0.9, {"lr": 0.002})
    best = cross.global_best()
    assert best is not None
    assert best["best_metric"] == 0.9


def test_global_best_none():
    config = SwarmConfig(num_agents=1, roles_distribution={"explorer": 1.0})
    cross = CrossRepoCoordinator(repo_paths=["/tmp/repo1"], config=config)
    cross.assign_all_roles()
    assert cross.global_best() is None
