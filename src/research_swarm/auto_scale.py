"""Auto-scaling: monitor CPU/memory and spawn/terminate agents."""

from typing import Any, Dict, Optional

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def get_resource_usage() -> Dict[str, float]:
    """Return current CPU and memory usage percentages."""
    if not HAS_PSUTIL:
        raise ImportError("psutil is required for auto-scaling: pip install psutil")
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "memory_percent": psutil.virtual_memory().percent,
    }


class AutoScaler:
    """Monitor resources and recommend agent count changes."""

    def __init__(
        self,
        cpu_upper: float = 80.0,
        cpu_lower: float = 20.0,
        max_agents: int = 16,
        min_agents: int = 1,
    ):
        self.cpu_upper = cpu_upper
        self.cpu_lower = cpu_lower
        self.max_agents = max_agents
        self.min_agents = min_agents

    def recommend(self, current_agents: int) -> int:
        """Return recommended number of agents based on current resource usage.

        Returns the same count if no change is needed.
        """
        if not HAS_PSUTIL:
            return current_agents
        usage = get_resource_usage()
        cpu = usage["cpu_percent"]
        if cpu > self.cpu_upper and current_agents > self.min_agents:
            return max(self.min_agents, current_agents - 1)
        elif cpu < self.cpu_lower and current_agents < self.max_agents:
            return min(self.max_agents, current_agents + 1)
        return current_agents
