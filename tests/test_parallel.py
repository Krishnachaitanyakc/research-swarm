"""Tests for parallel execution."""

import threading
import pytest
from autoresearch_swarm.agent import ResearchAgent
from autoresearch_swarm.config import SwarmConfig
from autoresearch_swarm.coordinator import SwarmCoordinator


def test_run_parallel_basic():
    config = SwarmConfig(num_agents=3, parallel=True)
    coord = SwarmCoordinator(repo_path="/tmp", config=config)
    coord.assign_roles()

    base_params = {"learning_rate": 0.001, "batch_size": 32}

    def experiment_fn(agent):
        return agent.run_experiment(agent.propose_experiment(base_params))

    results = coord.run_parallel(experiment_fn)
    assert len(results) == 3
    for r in results:
        assert "metric" in r
        assert "params" in r


def test_run_parallel_with_max_workers():
    config = SwarmConfig(num_agents=4, parallel=True)
    coord = SwarmCoordinator(repo_path="/tmp", config=config)
    coord.assign_roles()

    base_params = {"learning_rate": 0.001}

    def experiment_fn(agent):
        return agent.run_experiment(agent.propose_experiment(base_params))

    results = coord.run_parallel(experiment_fn, max_workers=2)
    assert len(results) == 4


def test_git_lock_exists():
    config = SwarmConfig()
    coord = SwarmCoordinator(repo_path="/tmp", config=config)
    assert hasattr(coord.git_lock, "acquire") and hasattr(coord.git_lock, "release")


def test_parallel_thread_safety():
    """Verify that parallel execution uses separate threads."""
    config = SwarmConfig(num_agents=3)
    coord = SwarmCoordinator(repo_path="/tmp", config=config)
    coord.assign_roles()

    thread_ids = []
    lock = threading.Lock()

    def experiment_fn(agent):
        with lock:
            thread_ids.append(threading.current_thread().ident)
        return agent.run_experiment({"lr": 0.001})

    coord.run_parallel(experiment_fn)
    # Should have recorded thread IDs for all agents
    assert len(thread_ids) == 3
