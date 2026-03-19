import pytest
from autoresearch_swarm.config import SwarmConfig


def test_default_config():
    config = SwarmConfig()
    assert config.num_agents == 3
    assert config.merge_interval == 300
    assert config.time_budget == 3600
    assert config.roles_distribution == {"explorer": 0.5, "exploiter": 0.3, "specialist": 0.2}


def test_custom_config():
    config = SwarmConfig(num_agents=8, time_budget=7200, merge_interval=600)
    assert config.num_agents == 8
    assert config.time_budget == 7200
    assert config.merge_interval == 600


def test_custom_roles():
    roles = {"explorer": 0.7, "exploiter": 0.3}
    config = SwarmConfig(roles_distribution=roles)
    assert config.roles_distribution == roles


def test_config_base_paths():
    config = SwarmConfig(base_train_py="train.py", prepare_py="prepare.py")
    assert config.base_train_py == "train.py"
    assert config.prepare_py == "prepare.py"
