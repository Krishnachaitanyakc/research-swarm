"""CLI for research-swarm."""

import json
import click

from research_swarm.config import SwarmConfig
from research_swarm.coordinator import SwarmCoordinator
from research_swarm.git_ops import create_agent_branch, list_agent_branches


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
@click.option("--parallel", is_flag=True, help="Run agents in parallel")
@click.option("--llm-guided", is_flag=True, help="Use LLM for strategy selection")
@click.option("--auto-scale", is_flag=True, help="Enable auto-scaling based on resources")
@click.option("--extra-repo", multiple=True, help="Additional repos for cross-repo coordination")
def run(repo, num_agents, time_budget, parallel, llm_guided, auto_scale, extra_repo):
    """Run swarm with N agents."""
    config = SwarmConfig(
        num_agents=num_agents,
        time_budget=time_budget,
        parallel=parallel,
        llm_guided=llm_guided,
        auto_scale=auto_scale,
        extra_repos=list(extra_repo),
    )

    if extra_repo:
        from research_swarm.cross_repo import CrossRepoCoordinator
        all_repos = [repo] + list(extra_repo)
        cross_coord = CrossRepoCoordinator(repo_paths=all_repos, config=config)
        repo_agents = cross_coord.assign_all_roles()
        click.echo(f"Cross-repo coordination across {len(all_repos)} repos")
        base_params = {"learning_rate": 0.001, "batch_size": 32}
        for repo_path, agents in repo_agents.items():
            click.echo(f"  Repo: {repo_path}")
            for agent in agents:
                result = agent.run_experiment(agent.propose_experiment(base_params))
                click.echo(f"    {agent.agent_id} ({agent.role}): metric={result['metric']:.4f}")
        best = cross_coord.global_best()
        if best:
            click.echo(f"Global best: {best['agent_id']} with metric={best['best_metric']:.4f}")
        return

    coord = SwarmCoordinator(repo_path=repo, config=config)
    agents = coord.assign_roles()
    click.echo(f"Running swarm with {len(agents)} agents for {time_budget}s")

    base_params = {"learning_rate": 0.001, "batch_size": 32}

    if parallel:
        def experiment_fn(agent):
            return agent.run_experiment(agent.propose_experiment(base_params))
        results = coord.run_parallel(experiment_fn)
        for r in results:
            click.echo(f"  metric={r['metric']:.4f}")
    else:
        for agent in agents:
            if llm_guided:
                from research_swarm.llm_strategy import suggest_strategy
                from research_swarm.agent import STRATEGY_MAP
                strategy = suggest_strategy(agent.history, list(STRATEGY_MAP.keys()))
                agent.switch_role(strategy)
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
    from research_swarm.results import SharedResultStore
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
    from research_swarm.git_ops import merge_to_main
    branches = list_agent_branches(repo)
    if not branches:
        click.echo("No agent branches found.")
        return
    for branch in branches:
        success = merge_to_main(repo, branch)
        status = "OK" if success else "CONFLICT"
        click.echo(f"  Merge {branch}: {status}")
