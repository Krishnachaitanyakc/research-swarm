"""Optional Pareto integration for multi-objective optimization."""

from typing import Any, Dict, List, Optional, Tuple

try:
    from autoresearch_pareto import ParetoFrontier  # type: ignore
    HAS_PARETO = True
except ImportError:
    HAS_PARETO = False


def is_dominated(point_a: List[float], point_b: List[float]) -> bool:
    """Return True if point_a is dominated by point_b (all dims worse or equal, at least one strictly worse)."""
    at_least_one_worse = False
    for a, b in zip(point_a, point_b):
        if a > b:
            return False
        if a < b:
            at_least_one_worse = True
    return at_least_one_worse


def compute_pareto_frontier(
    results: List[Dict[str, Any]],
    metric_keys: List[str],
) -> List[Dict[str, Any]]:
    """Compute the Pareto frontier from a list of results.

    If autoresearch-pareto is available, delegates to it. Otherwise uses
    a simple built-in implementation.
    """
    if not results or not metric_keys:
        return []

    if HAS_PARETO:
        frontier = ParetoFrontier()
        for r in results:
            metrics = {k: r.get(k, 0.0) for k in metric_keys}
            frontier.add(r, metrics)
        return frontier.get_frontier()

    # Built-in: extract metric vectors and filter dominated points
    points = []
    for r in results:
        vec = [r.get(k, 0.0) for k in metric_keys]
        points.append((vec, r))

    frontier = []
    for i, (vec_i, res_i) in enumerate(points):
        dominated = False
        for j, (vec_j, _) in enumerate(points):
            if i != j and is_dominated(vec_i, vec_j):
                dominated = True
                break
        if not dominated:
            frontier.append(res_i)
    return frontier


class MultiObjectiveTracker:
    """Track multi-objective metrics per agent."""

    def __init__(self, metric_keys: List[str]):
        self.metric_keys = metric_keys
        self._records: List[Dict[str, Any]] = []

    def record(self, agent_id: str, metrics: Dict[str, float], params: Dict[str, Any]) -> None:
        entry = {"agent_id": agent_id, "params": params}
        entry.update(metrics)
        self._records.append(entry)

    def get_frontier(self) -> List[Dict[str, Any]]:
        return compute_pareto_frontier(self._records, self.metric_keys)

    def should_merge(self, candidate: Dict[str, Any]) -> bool:
        """Return True if the candidate is on the Pareto frontier."""
        frontier = compute_pareto_frontier(
            self._records + [candidate], self.metric_keys
        )
        return candidate in frontier
