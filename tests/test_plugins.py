"""Tests for custom strategy plugins."""

import os
import tempfile
import pytest
from autoresearch_swarm.strategies import StrategyBase, load_plugins
from autoresearch_swarm.agent import STRATEGY_MAP, register_plugins


def test_strategy_base_is_abstract():
    with pytest.raises(TypeError):
        StrategyBase()


def test_builtin_strategies_are_subclasses():
    from autoresearch_swarm.strategies import ExplorerStrategy, ExploiterStrategy, SpecialistStrategy
    assert issubclass(ExplorerStrategy, StrategyBase)
    assert issubclass(ExploiterStrategy, StrategyBase)
    assert issubclass(SpecialistStrategy, StrategyBase)


def test_load_plugins_from_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        plugin_code = '''
from autoresearch_swarm.strategies import StrategyBase

class GeneticStrategy(StrategyBase):
    def generate(self, params, best_known=None):
        return {k: v * 2 for k, v in params.items()}
'''
        with open(os.path.join(tmpdir, "genetic.py"), "w") as f:
            f.write(plugin_code)
        plugins = load_plugins(tmpdir)
        assert "genetic" in plugins
        instance = plugins["genetic"]()
        result = instance.generate({"lr": 0.01})
        assert result["lr"] == 0.02


def test_load_plugins_empty_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        plugins = load_plugins(tmpdir)
        assert plugins == {}


def test_load_plugins_nonexistent_directory():
    plugins = load_plugins("/nonexistent/path")
    assert plugins == {}


def test_load_plugins_skips_non_strategy():
    with tempfile.TemporaryDirectory() as tmpdir:
        code = '''
class NotAStrategy:
    pass
'''
        with open(os.path.join(tmpdir, "helper.py"), "w") as f:
            f.write(code)
        plugins = load_plugins(tmpdir)
        assert len(plugins) == 0


def test_register_plugins():
    original_keys = set(STRATEGY_MAP.keys())
    with tempfile.TemporaryDirectory() as tmpdir:
        plugin_code = '''
from autoresearch_swarm.strategies import StrategyBase

class BayesianStrategy(StrategyBase):
    def generate(self, params, best_known=None):
        return params
'''
        with open(os.path.join(tmpdir, "bayesian.py"), "w") as f:
            f.write(plugin_code)
        register_plugins(tmpdir)
        assert "bayesian" in STRATEGY_MAP
    # Clean up
    for key in list(STRATEGY_MAP.keys()):
        if key not in original_keys:
            del STRATEGY_MAP[key]
