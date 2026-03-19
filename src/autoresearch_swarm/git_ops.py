"""Git operations for swarm coordination."""

import json
import os
import subprocess
from typing import Any, Dict, List, Optional


def _run_git(repo_path: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + list(args),
        cwd=repo_path,
        capture_output=True,
        text=True,
    )


def create_agent_branch(repo_path: str, agent_id: str) -> None:
    branch_name = f"agents/{agent_id}"
    _run_git(repo_path, "branch", branch_name)


def commit_experiment(
    repo_path: str, agent_id: str, description: str, files: List[str]
) -> None:
    branch_name = f"agents/{agent_id}"
    _run_git(repo_path, "checkout", branch_name)
    for f in files:
        _run_git(repo_path, "add", f)
    _run_git(repo_path, "commit", "-m", description)
    _run_git(repo_path, "checkout", "main")


def get_best_from_branch(repo_path: str, branch: str) -> Optional[Dict[str, Any]]:
    _run_git(repo_path, "checkout", branch)
    best_path = os.path.join(repo_path, "best.json")
    result = None
    if os.path.exists(best_path):
        with open(best_path) as f:
            result = json.load(f)
    _run_git(repo_path, "checkout", "main")
    return result


def merge_to_main(repo_path: str, branch: str) -> bool:
    _run_git(repo_path, "checkout", "main")
    result = _run_git(repo_path, "merge", branch, "--no-edit")
    return result.returncode == 0


def list_agent_branches(repo_path: str) -> List[str]:
    result = _run_git(repo_path, "branch", "--list", "agents/*")
    branches = []
    for line in result.stdout.strip().split("\n"):
        line = line.strip().lstrip("* ")
        if line.startswith("agents/"):
            branches.append(line)
    return branches
