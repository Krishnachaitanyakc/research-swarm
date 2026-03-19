"""Shared result store for aggregating results across agents."""

import json
import os
import time
from typing import Any, Dict, List, Optional


class SharedResultStore:
    def __init__(self, base_path: str):
        self.base_path = base_path

    def _agent_file(self, agent_id: str) -> str:
        return os.path.join(self.base_path, f"{agent_id}_results.json")

    def _message_file(self, agent_id: str) -> str:
        return os.path.join(self.base_path, f"{agent_id}_messages.json")

    def save_result(self, agent_id: str, metric: float, params: Dict[str, Any]) -> None:
        path = self._agent_file(agent_id)
        existing = []
        if os.path.exists(path):
            with open(path) as f:
                existing = json.load(f)
        existing.append({"metric": metric, "params": params, "agent_id": agent_id})
        with open(path, "w") as f:
            json.dump(existing, f, indent=2)

    def get_agent_results(self, agent_id: str) -> List[Dict[str, Any]]:
        path = self._agent_file(agent_id)
        if not os.path.exists(path):
            return []
        with open(path) as f:
            return json.load(f)

    def aggregate_results(self) -> List[Dict[str, Any]]:
        all_results = []
        for fname in os.listdir(self.base_path):
            if fname.endswith("_results.json"):
                with open(os.path.join(self.base_path, fname)) as f:
                    all_results.extend(json.load(f))
        return all_results

    def find_global_best(self) -> Optional[Dict[str, Any]]:
        results = self.aggregate_results()
        if not results:
            return None
        return max(results, key=lambda r: r["metric"])

    def save_message(self, from_id: str, to_id: str, content: str) -> None:
        path = self._message_file(to_id)
        existing = []
        if os.path.exists(path):
            with open(path) as f:
                existing = json.load(f)
        existing.append({
            "from": from_id,
            "to": to_id,
            "content": content,
            "timestamp": time.time(),
        })
        with open(path, "w") as f:
            json.dump(existing, f, indent=2)

    def get_messages(self, agent_id: str) -> List[Dict[str, Any]]:
        path = self._message_file(agent_id)
        if not os.path.exists(path):
            return []
        with open(path) as f:
            return json.load(f)

    def clear_messages(self, agent_id: str) -> None:
        path = self._message_file(agent_id)
        if os.path.exists(path):
            with open(path, "w") as f:
                json.dump([], f)
