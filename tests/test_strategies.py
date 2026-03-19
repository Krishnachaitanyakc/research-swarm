import pytest
from research_swarm.strategies import ExplorerStrategy, ExploiterStrategy, SpecialistStrategy


def test_explorer_strategy_modifies_params():
    strategy = ExplorerStrategy()
    params = {"learning_rate": 0.001, "batch_size": 32}
    new_params = strategy.generate(params)
    assert new_params != params
    assert set(new_params.keys()) == set(params.keys())


def test_explorer_strategy_randomness():
    strategy = ExplorerStrategy()
    params = {"learning_rate": 0.001, "batch_size": 32}
    results = [strategy.generate(params) for _ in range(10)]
    # Should produce some variety
    unique = len(set(str(r) for r in results))
    assert unique > 1


def test_exploiter_strategy_small_changes():
    strategy = ExploiterStrategy()
    params = {"learning_rate": 0.001, "batch_size": 32}
    new_params = strategy.generate(params)
    # Changes should be relatively small
    if "learning_rate" in new_params:
        ratio = new_params["learning_rate"] / params["learning_rate"]
        assert 0.5 < ratio < 2.0


def test_exploiter_with_best_known():
    strategy = ExploiterStrategy()
    params = {"learning_rate": 0.001, "batch_size": 32}
    best = {"learning_rate": 0.002, "batch_size": 64}
    new_params = strategy.generate(params, best_known=best)
    # Should be influenced by best_known
    assert isinstance(new_params, dict)


def test_specialist_strategy_one_param():
    strategy = SpecialistStrategy()
    params = {"learning_rate": 0.001, "batch_size": 32, "dropout": 0.1}
    new_params = strategy.generate(params)
    changed = sum(1 for k in params if new_params.get(k) != params[k])
    assert changed == 1


def test_specialist_strategy_focuses():
    strategy = SpecialistStrategy(focus_param="learning_rate")
    params = {"learning_rate": 0.001, "batch_size": 32, "dropout": 0.1}
    new_params = strategy.generate(params)
    assert new_params["batch_size"] == params["batch_size"]
    assert new_params["dropout"] == params["dropout"]
    assert new_params["learning_rate"] != params["learning_rate"]
