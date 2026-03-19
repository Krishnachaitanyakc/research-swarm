import os
import tempfile
import pytest
from autoresearch_swarm.results import SharedResultStore


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_store_creation(temp_dir):
    store = SharedResultStore(temp_dir)
    assert store.base_path == temp_dir


def test_save_agent_result(temp_dir):
    store = SharedResultStore(temp_dir)
    store.save_result("agent-1", 0.85, {"lr": 0.001})
    results = store.get_agent_results("agent-1")
    assert len(results) == 1
    assert results[0]["metric"] == 0.85


def test_save_multiple_results(temp_dir):
    store = SharedResultStore(temp_dir)
    store.save_result("agent-1", 0.85, {"lr": 0.001})
    store.save_result("agent-1", 0.90, {"lr": 0.002})
    results = store.get_agent_results("agent-1")
    assert len(results) == 2


def test_aggregate_results(temp_dir):
    store = SharedResultStore(temp_dir)
    store.save_result("agent-1", 0.85, {"lr": 0.001})
    store.save_result("agent-2", 0.90, {"lr": 0.002})
    store.save_result("agent-3", 0.80, {"lr": 0.003})
    agg = store.aggregate_results()
    assert len(agg) == 3


def test_find_global_best(temp_dir):
    store = SharedResultStore(temp_dir)
    store.save_result("agent-1", 0.85, {"lr": 0.001})
    store.save_result("agent-2", 0.90, {"lr": 0.002})
    store.save_result("agent-3", 0.80, {"lr": 0.003})
    best = store.find_global_best()
    assert best["metric"] == 0.90
    assert best["agent_id"] == "agent-2"


def test_empty_store(temp_dir):
    store = SharedResultStore(temp_dir)
    assert store.aggregate_results() == []
    assert store.find_global_best() is None
