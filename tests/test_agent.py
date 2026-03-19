import pytest
from autoresearch_swarm.agent import ResearchAgent


def test_agent_creation():
    agent = ResearchAgent(agent_id="agent-1", role="explorer")
    assert agent.agent_id == "agent-1"
    assert agent.role == "explorer"
    assert agent.current_branch == "agents/agent-1"
    assert agent.best_metric is None


def test_agent_propose_experiment():
    agent = ResearchAgent(agent_id="agent-1", role="explorer")
    experiment = agent.propose_experiment({"learning_rate": 0.001, "batch_size": 32})
    assert "learning_rate" in experiment or "batch_size" in experiment
    # Explorer should modify parameters
    assert experiment != {"learning_rate": 0.001, "batch_size": 32}


def test_agent_run_experiment():
    agent = ResearchAgent(agent_id="agent-1", role="explorer")
    result = agent.run_experiment({"learning_rate": 0.001, "batch_size": 32})
    assert "metric" in result
    assert "params" in result
    assert isinstance(result["metric"], float)


def test_agent_report_result():
    agent = ResearchAgent(agent_id="agent-1", role="explorer")
    agent.report_result(0.85, {"learning_rate": 0.001})
    assert agent.best_metric == 0.85
    assert len(agent.history) == 1


def test_agent_report_multiple_results():
    agent = ResearchAgent(agent_id="agent-1", role="explorer")
    agent.report_result(0.85, {"learning_rate": 0.001})
    agent.report_result(0.90, {"learning_rate": 0.002})
    agent.report_result(0.80, {"learning_rate": 0.003})
    assert agent.best_metric == 0.90
    assert len(agent.history) == 3


def test_agent_roles():
    for role in ["explorer", "exploiter", "specialist"]:
        agent = ResearchAgent(agent_id=f"agent-{role}", role=role)
        assert agent.role == role


def test_exploiter_refines_best():
    agent = ResearchAgent(agent_id="agent-2", role="exploiter")
    agent.report_result(0.85, {"learning_rate": 0.001, "batch_size": 32})
    experiment = agent.propose_experiment({"learning_rate": 0.001, "batch_size": 32})
    # Exploiter makes small changes
    assert "learning_rate" in experiment or "batch_size" in experiment


def test_specialist_focuses_single_param():
    agent = ResearchAgent(agent_id="agent-3", role="specialist")
    params = {"learning_rate": 0.001, "batch_size": 32, "dropout": 0.1}
    experiment = agent.propose_experiment(params)
    # Specialist changes only one parameter
    changed = sum(1 for k in params if experiment.get(k) != params[k])
    assert changed == 1
