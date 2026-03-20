# research-swarm

**Swarm intelligence for ML research.**

---

Single-agent research hits a wall: one strategy, one search path, one point of failure. **research-swarm** runs multiple research agents in parallel on separate git branches, each with a specialized role -- explorers cast a wide net, exploiters refine the best results, specialists drill into individual hyperparameters. A coordinator merges the best discoveries back to main.

## Quick Start

```bash
pip install research-swarm
```

```python
from research_swarm.coordinator import SwarmCoordinator
from research_swarm.config import SwarmConfig

config = SwarmConfig(num_agents=4, time_budget=3600)
coordinator = SwarmCoordinator(repo_path=".", config=config)
agents = coordinator.assign_roles()
best = coordinator.merge_best()
```

## Features

- **Multi-agent parallelism** -- run N agents simultaneously on separate git branches
- **Role specialization** -- Explorer (random perturbations), Exploiter (refine best), Specialist (single-param focus)
- **Git-based coordination** -- each agent works on `agents/<agent_id>/`, no shared state conflicts
- **Adaptive role switching** -- stagnant agents automatically switch strategies
- **LLM-guided strategy** -- optional Claude-powered strategy selection based on experiment history
- **Auto-scaling** -- dynamically adjust agent count based on available resources
- **Cross-repo coordination** -- orchestrate experiments across multiple repositories
- **Shared result store** -- aggregated results across all agents with global best tracking
- **Thread-safe** -- git operations protected by locks for safe parallel execution
- **Conflict resolution** -- automatic handling of merge conflicts between agent branches

## CLI Usage

```bash
# Initialize a swarm workspace with 4 agents
research-swarm init --repo /path/to/repo --num-agents 4

# Run the swarm
research-swarm run --repo . --num-agents 4 --time-budget 3600

# Run agents in parallel with LLM guidance
research-swarm run --repo . --num-agents 8 --parallel --llm-guided

# Auto-scale based on resources
research-swarm run --repo . --auto-scale --time-budget 7200

# Cross-repo coordination
research-swarm run --repo ./model-a --extra-repo ./model-b --extra-repo ./model-c

# Check agent statuses
research-swarm status --repo .

# View aggregated results
research-swarm results --repo .

# Manually merge best results to main
research-swarm merge --repo .
```

## Python API

```python
from research_swarm.agent import ResearchAgent
from research_swarm.coordinator import SwarmCoordinator
from research_swarm.config import SwarmConfig

# Configure and launch
config = SwarmConfig(num_agents=6, time_budget=3600, parallel=True)
coordinator = SwarmCoordinator(repo_path="/path/to/repo", config=config)
agents = coordinator.assign_roles()

# Run experiments in parallel
def experiment_fn(agent):
    params = agent.propose_experiment({"lr": 0.001, "batch_size": 32})
    return agent.run_experiment(params)

results = coordinator.run_parallel(experiment_fn)

# Adaptive role switching for stagnant agents
switched = coordinator.adapt_roles(stagnation_threshold=0.001, window=5)

# Merge the winning branch
best = coordinator.merge_best()
print(f"Best agent: {best['agent_id']} -- metric: {best['metric']:.4f}")
```

## Architecture

```
main
 |
 +-- agents/agent-1 (explorer)    -- random perturbations
 +-- agents/agent-2 (exploiter)   -- refines best known
 +-- agents/agent-3 (specialist)  -- drills into one param
 +-- agents/agent-4 (explorer)    -- independent search
 |
 v
coordinator merges best -> main
```

## Comparison

| Feature | research-swarm | Hyperspace AGI | CrewAI | Single-agent |
|---|---|---|---|---|
| Multiple parallel agents | Yes | Yes | Yes | No |
| Git-based coordination | Yes | No | No | N/A |
| Agent specialization | Explorer/Exploiter/Specialist | Generic | Role-based | N/A |
| Adaptive role switching | Yes | No | No | N/A |
| LLM-guided strategy | Yes | No | Yes | Varies |
| Cross-repo orchestration | Yes | No | No | No |
| Auto-scaling | Yes | No | No | No |
| Experiment-focused | Yes | General purpose | General purpose | Varies |
| Merge best to main | Automatic | N/A | N/A | N/A |

## License

MIT
