"""Swarm configuration."""

from dataclasses import dataclass, field
from typing import Dict, Optional


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
