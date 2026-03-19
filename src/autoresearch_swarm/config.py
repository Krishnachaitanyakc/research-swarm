"""Swarm configuration."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SwarmConfig:
    num_agents: int = 3
    roles_distribution: Dict[str, float] = field(default_factory=lambda: {
        "explorer": 0.5,
        "exploiter": 0.3,
        "specialist": 0.2,
    })
    merge_interval: int = 300
    time_budget: int = 3600
    base_train_py: Optional[str] = None
    prepare_py: Optional[str] = None
    # Adaptive role assignment
    adaptation_interval: int = 5
    stagnation_threshold: float = 0.001
    # Parallel execution
    parallel: bool = False
    max_workers: Optional[int] = None
    # Plugin directory
    strategy_plugin_dir: Optional[str] = None
    # LLM-guided strategy selection
    llm_guided: bool = False
    # Auto-scaling
    auto_scale: bool = False
    cpu_upper: float = 80.0
    cpu_lower: float = 20.0
    max_agents: int = 16
    min_agents: int = 1
    # Cross-repo coordination
    extra_repos: List[str] = field(default_factory=list)
    # SSH distributed execution
    ssh_machines: List[Dict[str, str]] = field(default_factory=list)
