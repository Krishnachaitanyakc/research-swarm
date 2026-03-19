"""Git operations for swarm coordination."""

import json
import logging
import os
import subprocess
import threading
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_git_lock = threading.Lock()


def _run_git(repo_path: str, *args: str, lock: Optional[threading.Lock] = None) -> subprocess.CompletedProcess:
    target_lock = lock or _git_lock
    with target_lock:
        return subprocess.run(
            ["git"] + list(args),
            cwd=repo_path,
            capture_output=True,
            text=True,
        )


def create_agent_branch(repo_path: str, agent_id: str, lock: Optional[threading.Lock] = None) -> None:
    branch_name = f"agents/{agent_id}"
    _run_git(repo_path, "branch", branch_name, lock=lock)


def commit_experiment(
    repo_path: str, agent_id: str, description: str, files: List[str],
    lock: Optional[threading.Lock] = None,
) -> None:
    branch_name = f"agents/{agent_id}"
    _run_git(repo_path, "checkout", branch_name, lock=lock)
    for f in files:
        _run_git(repo_path, "add", f, lock=lock)
    _run_git(repo_path, "commit", "-m", description, lock=lock)
    _run_git(repo_path, "checkout", "main", lock=lock)


def get_best_from_branch(repo_path: str, branch: str, lock: Optional[threading.Lock] = None) -> Optional[Dict[str, Any]]:
    _run_git(repo_path, "checkout", branch, lock=lock)
    best_path = os.path.join(repo_path, "best.json")
    result = None
    if os.path.exists(best_path):
        with open(best_path) as f:
            result = json.load(f)
    _run_git(repo_path, "checkout", "main", lock=lock)
    return result


def merge_to_main(
    repo_path: str, branch: str, lock: Optional[threading.Lock] = None,
    conflict_log: Optional[str] = None,
) -> bool:
    _run_git(repo_path, "checkout", "main", lock=lock)
    result = _run_git(repo_path, "merge", branch, "--no-edit", lock=lock)
    if result.returncode == 0:
        return True
    # Conflict detected
    log_path = conflict_log or os.path.join(repo_path, "conflicts.log")
    msg = f"Conflict merging {branch}: {result.stderr.strip()}\n"
    logger.warning(msg)
    with open(log_path, "a") as f:
        f.write(msg)
    # Abort the failed merge
    _run_git(repo_path, "merge", "--abort", lock=lock)
    return False


def list_agent_branches(repo_path: str, lock: Optional[threading.Lock] = None) -> List[str]:
    result = _run_git(repo_path, "branch", "--list", "agents/*", lock=lock)
    branches = []
    for line in result.stdout.strip().split("\n"):
        line = line.strip().lstrip("* ")
        if line.startswith("agents/"):
            branches.append(line)
    return branches
