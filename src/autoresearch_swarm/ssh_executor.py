"""Distributed SSH executor for running agents on remote machines."""

import json
import os
import tempfile
from typing import Any, Dict, List, Optional

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False


class SSHExecutor:
    """Connect to a remote machine, clone repo, run agent, collect results."""

    def __init__(
        self,
        host: str,
        username: str,
        key_path: Optional[str] = None,
        port: int = 22,
    ):
        if not HAS_PARAMIKO:
            raise ImportError("paramiko is required for SSH execution: pip install paramiko")
        self.host = host
        self.username = username
        self.key_path = key_path
        self.port = port
        self._client: Optional["paramiko.SSHClient"] = None

    def connect(self) -> None:
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        kwargs: Dict[str, Any] = {
            "hostname": self.host,
            "username": self.username,
            "port": self.port,
        }
        if self.key_path:
            kwargs["key_filename"] = self.key_path
        self._client.connect(**kwargs)

    def disconnect(self) -> None:
        if self._client:
            self._client.close()
            self._client = None

    def run_command(self, command: str) -> Dict[str, Any]:
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")
        stdin, stdout, stderr = self._client.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()
        return {
            "stdout": stdout.read().decode(),
            "stderr": stderr.read().decode(),
            "exit_code": exit_code,
        }

    def clone_and_run(
        self,
        repo_url: str,
        agent_id: str,
        role: str = "explorer",
        remote_dir: str = "/tmp/autoresearch-swarm",
    ) -> Dict[str, Any]:
        self.run_command(f"rm -rf {remote_dir} && git clone {repo_url} {remote_dir}")
        cmd = (
            f"cd {remote_dir} && "
            f"pip install -e . 2>/dev/null && "
            f"autoresearch-swarm run --repo {remote_dir} --num-agents 1"
        )
        return self.run_command(cmd)

    def fetch_results(
        self,
        remote_path: str,
        local_path: str,
    ) -> None:
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")
        sftp = self._client.open_sftp()
        try:
            sftp.get(remote_path, local_path)
        finally:
            sftp.close()

    @classmethod
    def from_config(cls, machine_config: Dict[str, str]) -> "SSHExecutor":
        return cls(
            host=machine_config["host"],
            username=machine_config["username"],
            key_path=machine_config.get("key_path"),
            port=int(machine_config.get("port", 22)),
        )
