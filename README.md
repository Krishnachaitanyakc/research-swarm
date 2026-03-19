# research-swarm

Multi-agent distributed research with git-based coordination. Multiple research agents work in parallel on different git branches, each following the autoresearch loop. A coordinator periodically collects and merges the best results.

## Features

- Multiple agents work in parallel on different git branches
- Agent specialization: Explorer (random perturbations), Exploiter (refine best), Specialist (focus on one hyperparameter)
- Coordinator periodically collects and merges best results to main
- Git branch structure: `agents/<agent_id>/`
- Aggregated results across all agents via SharedResultStore

## Installation

```bash
pip install -e .
```

## Usage

### CLI

```bash
# Initialize a swarm workspace
research-swarm init --repo /path/to/repo

# Run swarm with 4 agents
research-swarm run --num-agents 4 --time-budget 3600

# Check agent statuses
research-swarm status

# View aggregated results
research-swarm results

# Manually trigger merge of best results
research-swarm merge
```

### Python API

```python
from research_swarm.agent import ResearchAgent
from research_swarm.coordinator import SwarmCoordinator
from research_swarm.config import SwarmConfig

config = SwarmConfig(num_agents=4, time_budget=3600)
coordinator = SwarmCoordinator(repo_path="/path/to/repo", config=config)

# Register agents
agent = ResearchAgent(agent_id="agent-1", role="explorer")
coordinator.register_agent(agent)

# Run the swarm
coordinator.assign_roles()
results = coordinator.collect_results()
coordinator.merge_best()
```
