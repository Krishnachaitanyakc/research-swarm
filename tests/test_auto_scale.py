"""Tests for auto-scaling."""

import pytest
from unittest.mock import patch, MagicMock
from research_swarm.auto_scale import AutoScaler, HAS_PSUTIL


def test_autoscaler_creation():
    scaler = AutoScaler(cpu_upper=80.0, cpu_lower=20.0)
    assert scaler.cpu_upper == 80.0
    assert scaler.cpu_lower == 20.0


def test_recommend_no_change_without_psutil():
    with patch("research_swarm.auto_scale.HAS_PSUTIL", False):
        scaler = AutoScaler()
        assert scaler.recommend(3) == 3


@patch("research_swarm.auto_scale.HAS_PSUTIL", True)
@patch("research_swarm.auto_scale.get_resource_usage")
def test_recommend_scale_down(mock_usage):
    mock_usage.return_value = {"cpu_percent": 90.0, "memory_percent": 50.0}
    scaler = AutoScaler(cpu_upper=80.0, min_agents=1)
    assert scaler.recommend(3) == 2


@patch("research_swarm.auto_scale.HAS_PSUTIL", True)
@patch("research_swarm.auto_scale.get_resource_usage")
def test_recommend_scale_up(mock_usage):
    mock_usage.return_value = {"cpu_percent": 10.0, "memory_percent": 30.0}
    scaler = AutoScaler(cpu_lower=20.0, max_agents=8)
    assert scaler.recommend(3) == 4


@patch("research_swarm.auto_scale.HAS_PSUTIL", True)
@patch("research_swarm.auto_scale.get_resource_usage")
def test_recommend_no_change(mock_usage):
    mock_usage.return_value = {"cpu_percent": 50.0, "memory_percent": 50.0}
    scaler = AutoScaler()
    assert scaler.recommend(3) == 3


@patch("research_swarm.auto_scale.HAS_PSUTIL", True)
@patch("research_swarm.auto_scale.get_resource_usage")
def test_recommend_respects_min(mock_usage):
    mock_usage.return_value = {"cpu_percent": 95.0, "memory_percent": 90.0}
    scaler = AutoScaler(min_agents=1)
    assert scaler.recommend(1) == 1


@patch("research_swarm.auto_scale.HAS_PSUTIL", True)
@patch("research_swarm.auto_scale.get_resource_usage")
def test_recommend_respects_max(mock_usage):
    mock_usage.return_value = {"cpu_percent": 5.0, "memory_percent": 10.0}
    scaler = AutoScaler(max_agents=4)
    assert scaler.recommend(4) == 4
