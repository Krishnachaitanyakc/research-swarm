"""Tests for adaptive role assignment and convergence tracking."""

import pytest
from autoresearch_swarm.agent import ResearchAgent
from autoresearch_swarm.config import SwarmConfig
from autoresearch_swarm.coordinator import SwarmCoordinator


def test_convergence_rate_empty():
    agent = ResearchAgent("agent-1", role="explorer")
    assert agent.convergence_rate() == 0.0


def test_convergence_rate_single():
    agent = ResearchAgent("agent-1", role="explorer")
    agent.report_result(0.5, {"lr": 0.001})
    assert agent.convergence_rate() == 0.0


def test_convergence_rate_improving():
    agent = ResearchAgent("agent-1", role="explorer")
    for i in range(5):
        agent.report_result(0.5 + i * 0.1, {"lr": 0.001})
    rate = agent.convergence_rate(window=5)
    assert rate > 0


def test_convergence_rate_stagnant():
    agent = ResearchAgent("agent-1", role="explorer")
    for _ in range(5):
        agent.report_result(0.5, {"lr": 0.001})
    rate = agent.convergence_rate(window=5)
    assert rate == 0.0


def test_switch_role():
    agent = ResearchAgent("agent-1", role="explorer")
    assert agent.role == "explorer"
    agent.switch_role("exploiter")
    assert agent.role == "exploiter"


def test_adapt_roles_switches_stagnant():
    config = SwarmConfig(num_agents=2, roles_distribution={"explorer": 0.5, "exploiter": 0.5})
    coord = SwarmCoordinator(repo_path="/tmp", config=config)
    agents = coord.assign_roles()

    # Make first agent stagnant
    for _ in range(5):
        agents[0].report_result(0.5, {"lr": 0.001})
    # Make second agent improving
    for i in range(5):
        agents[1].report_result(0.5 + i * 0.1, {"lr": 0.001})

    switched = coord.adapt_roles(stagnation_threshold=0.001, window=5)
    assert agents[0].agent_id in switched
    assert agents[1].agent_id not in switched


def test_adapt_roles_explorer_becomes_exploiter():
    config = SwarmConfig(num_agents=1, roles_distribution={"explorer": 1.0})
    coord = SwarmCoordinator(repo_path="/tmp", config=config)
    agents = coord.assign_roles()
    for _ in range(5):
        agents[0].report_result(0.5, {"lr": 0.001})
    coord.adapt_roles(window=5)
    assert agents[0].role == "exploiter"


def test_adapt_roles_exploiter_becomes_explorer():
    config = SwarmConfig(num_agents=1, roles_distribution={"exploiter": 1.0})
    coord = SwarmCoordinator(repo_path="/tmp", config=config)
    agents = coord.assign_roles()
    for _ in range(5):
        agents[0].report_result(0.5, {"lr": 0.001})
    coord.adapt_roles(window=5)
    assert agents[0].role == "explorer"
