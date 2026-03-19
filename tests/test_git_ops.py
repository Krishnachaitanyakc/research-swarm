import os
import json
import tempfile
import pytest
from autoresearch_swarm.git_ops import (
    create_agent_branch,
    commit_experiment,
    get_best_from_branch,
    merge_to_main,
    list_agent_branches,
)


@pytest.fixture
def temp_git_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.system(f"cd {tmpdir} && git init && git checkout -b main")
        # Create initial commit
        with open(os.path.join(tmpdir, "README.md"), "w") as f:
            f.write("# Test repo\n")
        os.system(f'cd {tmpdir} && git add README.md && git commit -m "initial commit"')
        yield tmpdir


def test_create_agent_branch(temp_git_repo):
    create_agent_branch(temp_git_repo, "agent-1")
    import subprocess
    result = subprocess.run(
        ["git", "branch", "--list", "agents/agent-1"],
        cwd=temp_git_repo, capture_output=True, text=True
    )
    assert "agents/agent-1" in result.stdout


def test_commit_experiment(temp_git_repo):
    create_agent_branch(temp_git_repo, "agent-1")
    # Write a file to commit
    with open(os.path.join(temp_git_repo, "experiment.json"), "w") as f:
        json.dump({"lr": 0.001}, f)
    commit_experiment(temp_git_repo, "agent-1", "test experiment", ["experiment.json"])
    import subprocess
    result = subprocess.run(
        ["git", "log", "--oneline", "agents/agent-1"],
        cwd=temp_git_repo, capture_output=True, text=True
    )
    assert "test experiment" in result.stdout


def test_get_best_from_branch(temp_git_repo):
    create_agent_branch(temp_git_repo, "agent-1")
    best_data = {"metric": 0.95, "params": {"lr": 0.001}}
    with open(os.path.join(temp_git_repo, "best.json"), "w") as f:
        json.dump(best_data, f)
    commit_experiment(temp_git_repo, "agent-1", "best result", ["best.json"])
    result = get_best_from_branch(temp_git_repo, "agents/agent-1")
    assert result is not None
    assert result["metric"] == 0.95


def test_list_agent_branches(temp_git_repo):
    create_agent_branch(temp_git_repo, "agent-1")
    create_agent_branch(temp_git_repo, "agent-2")
    branches = list_agent_branches(temp_git_repo)
    assert "agents/agent-1" in branches
    assert "agents/agent-2" in branches


def test_merge_to_main(temp_git_repo):
    create_agent_branch(temp_git_repo, "agent-1")
    with open(os.path.join(temp_git_repo, "result.txt"), "w") as f:
        f.write("best result\n")
    commit_experiment(temp_git_repo, "agent-1", "best result", ["result.txt"])
    success = merge_to_main(temp_git_repo, "agents/agent-1")
    assert success is True
