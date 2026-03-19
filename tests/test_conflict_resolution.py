"""Tests for conflict resolution in git operations."""

import json
import os
import tempfile
import pytest
from autoresearch_swarm.git_ops import (
    create_agent_branch,
    commit_experiment,
    merge_to_main,
    _run_git,
)


@pytest.fixture
def temp_git_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.system(f"cd {tmpdir} && git init && git checkout -b main")
        with open(os.path.join(tmpdir, "README.md"), "w") as f:
            f.write("# Test repo\n")
        os.system(f'cd {tmpdir} && git add README.md && git commit -m "initial commit"')
        yield tmpdir


def test_merge_conflict_detected(temp_git_repo):
    create_agent_branch(temp_git_repo, "agent-1")
    create_agent_branch(temp_git_repo, "agent-2")

    # Create conflicting changes on agent-1
    _run_git(temp_git_repo, "checkout", "agents/agent-1")
    with open(os.path.join(temp_git_repo, "result.txt"), "w") as f:
        f.write("agent-1 result\n")
    _run_git(temp_git_repo, "add", "result.txt")
    _run_git(temp_git_repo, "commit", "-m", "agent-1 result")
    _run_git(temp_git_repo, "checkout", "main")

    # Create conflicting changes on agent-2
    _run_git(temp_git_repo, "checkout", "agents/agent-2")
    with open(os.path.join(temp_git_repo, "result.txt"), "w") as f:
        f.write("agent-2 result\n")
    _run_git(temp_git_repo, "add", "result.txt")
    _run_git(temp_git_repo, "commit", "-m", "agent-2 result")
    _run_git(temp_git_repo, "checkout", "main")

    # Merge first branch (should succeed)
    assert merge_to_main(temp_git_repo, "agents/agent-1") is True

    # Merge second branch (should conflict)
    assert merge_to_main(temp_git_repo, "agents/agent-2") is False


def test_conflict_log_created(temp_git_repo):
    create_agent_branch(temp_git_repo, "agent-1")
    create_agent_branch(temp_git_repo, "agent-2")

    _run_git(temp_git_repo, "checkout", "agents/agent-1")
    with open(os.path.join(temp_git_repo, "data.txt"), "w") as f:
        f.write("version A\n")
    _run_git(temp_git_repo, "add", "data.txt")
    _run_git(temp_git_repo, "commit", "-m", "agent-1 data")
    _run_git(temp_git_repo, "checkout", "main")

    _run_git(temp_git_repo, "checkout", "agents/agent-2")
    with open(os.path.join(temp_git_repo, "data.txt"), "w") as f:
        f.write("version B\n")
    _run_git(temp_git_repo, "add", "data.txt")
    _run_git(temp_git_repo, "commit", "-m", "agent-2 data")
    _run_git(temp_git_repo, "checkout", "main")

    merge_to_main(temp_git_repo, "agents/agent-1")
    log_path = os.path.join(temp_git_repo, "conflicts.log")
    merge_to_main(temp_git_repo, "agents/agent-2", conflict_log=log_path)
    assert os.path.exists(log_path)
    with open(log_path) as f:
        content = f.read()
    assert "agents/agent-2" in content


def test_merge_abort_after_conflict(temp_git_repo):
    """After a conflict, the repo should be in a clean state (merge aborted)."""
    create_agent_branch(temp_git_repo, "agent-1")
    create_agent_branch(temp_git_repo, "agent-2")

    _run_git(temp_git_repo, "checkout", "agents/agent-1")
    with open(os.path.join(temp_git_repo, "x.txt"), "w") as f:
        f.write("A\n")
    _run_git(temp_git_repo, "add", "x.txt")
    _run_git(temp_git_repo, "commit", "-m", "a1")
    _run_git(temp_git_repo, "checkout", "main")

    _run_git(temp_git_repo, "checkout", "agents/agent-2")
    with open(os.path.join(temp_git_repo, "x.txt"), "w") as f:
        f.write("B\n")
    _run_git(temp_git_repo, "add", "x.txt")
    _run_git(temp_git_repo, "commit", "-m", "a2")
    _run_git(temp_git_repo, "checkout", "main")

    merge_to_main(temp_git_repo, "agents/agent-1")
    merge_to_main(temp_git_repo, "agents/agent-2")

    # Should be able to run git status cleanly (no MERGING state)
    result = _run_git(temp_git_repo, "status")
    assert "Unmerged" not in result.stdout
