"""Swarm coordinator that manages agents and merges results."""

import math
from typing import Any, Dict, List

from autoresearch_swarm.agent import ResearchAgent
from autoresearch_swarm.config import SwarmConfig


class SwarmCoordinator:
    def __init__(self, repo_path: str, config: SwarmConfig):
        self.repo_path = repo_path
        self.config = config
        self.agents: List[ResearchAgent] = []

    def register_agent(self, agent: ResearchAgent) -> None:
        self.agents.append(agent)

    def assign_roles(self) -> List[ResearchAgent]:
        roles_dist = self.config.roles_distribution
        n = self.config.num_agents
        agents = []
        role_items = sorted(roles_dist.items(), key=lambda x: -x[1])
        assigned = 0
        for i, (role, frac) in enumerate(role_items):
            if i == len(role_items) - 1:
                count = n - assigned
            else:
                count = max(1, round(n * frac))
                count = min(count, n - assigned - (len(role_items) - i - 1))
            for j in range(count):
                agent_id = f"agent-{assigned + j + 1}"
                agent = ResearchAgent(agent_id=agent_id, role=role)
                agents.append(agent)
                self.register_agent(agent)
            assigned += count
        return agents

    def collect_results(self) -> List[Dict[str, Any]]:
        results = []
        for agent in self.agents:
            results.append({
                "agent_id": agent.agent_id,
                "role": agent.role,
                "best_metric": agent.best_metric,
                "best_params": agent.best_params,
                "num_experiments": len(agent.history),
            })
        return results

    def merge_best(self) -> Dict[str, Any]:
        best_agent = None
        best_metric = None
        for agent in self.agents:
            if agent.best_metric is not None:
                if best_metric is None or agent.best_metric > best_metric:
                    best_metric = agent.best_metric
                    best_agent = agent
        if best_agent is None:
            return {"agent_id": None, "metric": None}
        return {
            "agent_id": best_agent.agent_id,
            "metric": best_agent.best_metric,
            "params": best_agent.best_params,
        }
