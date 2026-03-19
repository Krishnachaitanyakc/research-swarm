import os
import tempfile
import pytest
from research_swarm.agent import ResearchAgent
from research_swarm.coordinator import SwarmCoordinator
from research_swarm.config import SwarmConfig


@pytest.fixture
def temp_git_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.system(f"cd {tmpdir} && git init && git checkout -b main")
        with open(os.path.join(tmpdir, "README.md"), "w") as f:
            f.write("# Test repo\n")
        os.system(f'cd {tmpdir} && git add README.md && git commit -m "initial commit"')
        yield tmpdir


def test_coordinator_creation(temp_git_repo):
    config = SwarmConfig(num_agents=3)
    coord = SwarmCoordinator(repo_path=temp_git_repo, config=config)
    assert coord.repo_path == temp_git_repo
    assert len(coord.agents) == 0


def test_register_agent(temp_git_repo):
    config = SwarmConfig()
    coord = SwarmCoordinator(repo_path=temp_git_repo, config=config)
    agent = ResearchAgent(agent_id="agent-1", role="explorer")
    coord.register_agent(agent)
    assert len(coord.agents) == 1
    assert coord.agents[0].agent_id == "agent-1"


def test_assign_roles(temp_git_repo):
    config = SwarmConfig(num_agents=4)
    coord = SwarmCoordinator(repo_path=temp_git_repo, config=config)
    agents = coord.assign_roles()
    assert len(agents) == 4
    roles = [a.role for a in agents]
    assert "explorer" in roles


def test_collect_results(temp_git_repo):
    config = SwarmConfig()
    coord = SwarmCoordinator(repo_path=temp_git_repo, config=config)
    agent = ResearchAgent(agent_id="agent-1", role="explorer")
    agent.report_result(0.85, {"lr": 0.001})
    coord.register_agent(agent)
    results = coord.collect_results()
    assert len(results) == 1
    assert results[0]["best_metric"] == 0.85


def test_merge_best(temp_git_repo):
    config = SwarmConfig()
    coord = SwarmCoordinator(repo_path=temp_git_repo, config=config)
    agent1 = ResearchAgent(agent_id="agent-1", role="explorer")
    agent1.report_result(0.85, {"lr": 0.001})
    agent2 = ResearchAgent(agent_id="agent-2", role="exploiter")
    agent2.report_result(0.90, {"lr": 0.002})
    coord.register_agent(agent1)
    coord.register_agent(agent2)
    best = coord.merge_best()
    assert best["agent_id"] == "agent-2"
    assert best["metric"] == 0.90
