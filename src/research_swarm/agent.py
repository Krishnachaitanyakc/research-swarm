"""Research agent that proposes, runs, and reports experiments."""

import random
from typing import Any, Dict, List, Optional

from research_swarm.strategies import (
    ExplorerStrategy,
    ExploiterStrategy,
    SpecialistStrategy,
    StrategyBase,
    load_plugins,
)


STRATEGY_MAP: Dict[str, type] = {
    "explorer": ExplorerStrategy,
    "exploiter": ExploiterStrategy,
    "specialist": SpecialistStrategy,
}


def register_plugins(directory: str) -> None:
    """Load strategy plugins from a directory and add them to STRATEGY_MAP."""
    plugins = load_plugins(directory)
    STRATEGY_MAP.update(plugins)


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

    def convergence_rate(self, window: int = 5) -> float:
        """Compute improvement slope over the last `window` experiments.

        Returns 0.0 when there is not enough history. A positive value means
        the agent is still improving; near-zero or negative means stagnation.
        """
        if len(self.history) < 2:
            return 0.0
        recent = self.history[-window:]
        if len(recent) < 2:
            return 0.0
        n = len(recent)
        xs = list(range(n))
        ys = [r["metric"] for r in recent]
        x_mean = sum(xs) / n
        y_mean = sum(ys) / n
        num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
        den = sum((x - x_mean) ** 2 for x in xs)
        if den == 0:
            return 0.0
        return num / den

    def switch_role(self, new_role: str) -> None:
        """Switch this agent's role and strategy."""
        self.role = new_role
        self._strategy = STRATEGY_MAP.get(new_role, ExplorerStrategy)()
