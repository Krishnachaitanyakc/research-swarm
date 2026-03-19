"""Tests for SSH executor (unit tests without actual SSH)."""

import pytest
from unittest.mock import patch, MagicMock
from research_swarm.ssh_executor import SSHExecutor, HAS_PARAMIKO


@pytest.mark.skipif(not HAS_PARAMIKO, reason="paramiko not installed")
def test_ssh_executor_creation():
    executor = SSHExecutor(host="example.com", username="user")
    assert executor.host == "example.com"
    assert executor.username == "user"
    assert executor.port == 22


@pytest.mark.skipif(not HAS_PARAMIKO, reason="paramiko not installed")
def test_ssh_executor_from_config():
    config = {"host": "10.0.0.1", "username": "admin", "port": "2222"}
    executor = SSHExecutor.from_config(config)
    assert executor.host == "10.0.0.1"
    assert executor.port == 2222


@pytest.mark.skipif(not HAS_PARAMIKO, reason="paramiko not installed")
def test_run_command_not_connected():
    executor = SSHExecutor(host="example.com", username="user")
    with pytest.raises(RuntimeError, match="Not connected"):
        executor.run_command("ls")


@pytest.mark.skipif(not HAS_PARAMIKO, reason="paramiko not installed")
def test_disconnect_when_not_connected():
    executor = SSHExecutor(host="example.com", username="user")
    # Should not raise
    executor.disconnect()


def test_import_error_without_paramiko():
    with patch("research_swarm.ssh_executor.HAS_PARAMIKO", False):
        from research_swarm.ssh_executor import SSHExecutor as SE
        with pytest.raises(ImportError, match="paramiko"):
            SE(host="example.com", username="user")
