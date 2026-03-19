"""CLI for autoresearch-swarm."""

import json
import click

from autoresearch_swarm.config import SwarmConfig
from autoresearch_swarm.coordinator import SwarmCoordinator
from autoresearch_swarm.git_ops import create_agent_branch, list_agent_branches


@click.group()
def cli():
    """Multi-agent distributed research with git-based coordination."""
    pass


@cli.command()
@click.option("--repo", required=True, help="Path to git repository")
@click.option("--num-agents", default=3, help="Number of agents")
def init(repo, num_agents):
    """Initialize a swarm workspace."""
    config = SwarmConfig(num_agents=num_agents)
    coord = SwarmCoordinator(repo_path=repo, config=config)
    agents = coord.assign_roles()
    for agent in agents:
        create_agent_branch(repo, agent.agent_id)
    click.echo(f"Initialized swarm with {len(agents)} agents")
    for agent in agents:
        click.echo(f"  {agent.agent_id}: {agent.role} -> {agent.current_branch}")


@cli.command()
@click.option("--repo", required=True, help="Path to git repository")
@click.option("--num-agents", default=3, help="Number of agents")
@click.option("--time-budget", default=3600, help="Time budget in seconds")
def run(repo, num_agents, time_budget):
    """Run swarm with N agents."""
    config = SwarmConfig(num_agents=num_agents, time_budget=time_budget)
    coord = SwarmCoordinator(repo_path=repo, config=config)
    agents = coord.assign_roles()
    click.echo(f"Running swarm with {len(agents)} agents for {time_budget}s")
    # Simulate one round of experiments
    base_params = {"learning_rate": 0.001, "batch_size": 32}
    for agent in agents:
        result = agent.run_experiment(agent.propose_experiment(base_params))
        click.echo(f"  {agent.agent_id} ({agent.role}): metric={result['metric']:.4f}")
    best = coord.merge_best()
    click.echo(f"Best: {best['agent_id']} with metric={best['metric']:.4f}")


@cli.command()
@click.option("--repo", required=True, help="Path to git repository")
def status(repo):
    """Show agent statuses."""
    branches = list_agent_branches(repo)
    click.echo(f"Agent branches ({len(branches)}):")
    for b in branches:
        click.echo(f"  {b}")


@cli.command()
@click.option("--repo", required=True, help="Path to git repository")
def results(repo):
    """Show aggregated results."""
    from autoresearch_swarm.results import SharedResultStore
    store = SharedResultStore(repo)
    all_results = store.aggregate_results()
    if not all_results:
        click.echo("No results yet.")
        return
    for r in sorted(all_results, key=lambda x: -x["metric"]):
        click.echo(f"  {r['agent_id']}: metric={r['metric']:.4f} params={r['params']}")
    best = store.find_global_best()
    if best:
        click.echo(f"Global best: {best['agent_id']} metric={best['metric']:.4f}")


@cli.command()
@click.option("--repo", required=True, help="Path to git repository")
def merge(repo):
    """Manually trigger merge of best results."""
    from autoresearch_swarm.git_ops import merge_to_main
    branches = list_agent_branches(repo)
    if not branches:
        click.echo("No agent branches found.")
        return
    for branch in branches:
        success = merge_to_main(repo, branch)
        status = "OK" if success else "CONFLICT"
        click.echo(f"  Merge {branch}: {status}")
