"""Research agent that proposes, runs, and reports experiments."""

import random
from typing import Any, Dict, List, Optional

from autoresearch_swarm.strategies import ExplorerStrategy, ExploiterStrategy, SpecialistStrategy


STRATEGY_MAP = {
    "explorer": ExplorerStrategy,
    "exploiter": ExploiterStrategy,
    "specialist": SpecialistStrategy,
}


class ResearchAgent:
    def __init__(self, agent_id: str, role: str = "explorer"):
        self.agent_id = agent_id
        self.role = role
        self.current_branch = f"agents/{agent_id}"
        self.best_metric: Optional[float] = None
        self.best_params: Optional[Dict[str, Any]] = None
        self.history: List[Dict[str, Any]] = []
        self._strategy = STRATEGY_MAP.get(role, ExplorerStrategy)()

    def propose_experiment(self, current_params: Dict[str, Any]) -> Dict[str, Any]:
        return self._strategy.generate(current_params, best_known=self.best_params)

    def run_experiment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Simulate running an experiment - returns a mock metric
        metric = random.uniform(0.5, 1.0)
        self.report_result(metric, params)
        return {"metric": metric, "params": params}

    def report_result(self, metric: float, params: Dict[str, Any]) -> None:
        self.history.append({"metric": metric, "params": params})
        if self.best_metric is None or metric > self.best_metric:
            self.best_metric = metric
            self.best_params = dict(params)
