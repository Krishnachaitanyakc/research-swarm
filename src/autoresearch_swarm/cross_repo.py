"""Cross-repo coordination: manage agents across multiple repositories."""

from typing import Any, Dict, List, Optional

from autoresearch_swarm.config import SwarmConfig
from autoresearch_swarm.coordinator import SwarmCoordinator


class CrossRepoCoordinator:
    """Manages SwarmCoordinators across multiple repos and aggregates results."""

    def __init__(self, repo_paths: List[str], config: SwarmConfig):
        self.repo_paths = repo_paths
        self.config = config
        self.coordinators: List[SwarmCoordinator] = []
        for path in repo_paths:
            self.coordinators.append(SwarmCoordinator(repo_path=path, config=config))

    def assign_all_roles(self) -> Dict[str, List[Any]]:
        """Assign roles for each repo coordinator. Returns map of repo->agents."""
        result = {}
        for coord in self.coordinators:
            agents = coord.assign_roles()
            result[coord.repo_path] = agents
        return result

    def collect_all_results(self) -> List[Dict[str, Any]]:
        """Aggregate results from all repos."""
        all_results = []
        for coord in self.coordinators:
            for entry in coord.collect_results():
                entry["repo_path"] = coord.repo_path
                all_results.append(entry)
        return all_results

    def global_best(self) -> Optional[Dict[str, Any]]:
        """Find the global best across all repos."""
        all_results = self.collect_all_results()
        valid = [r for r in all_results if r.get("best_metric") is not None]
        if not valid:
            return None
        return max(valid, key=lambda r: r["best_metric"])
