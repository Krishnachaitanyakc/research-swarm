"""LLM-guided strategy selection using Anthropic Claude."""

import json
from typing import Any, Dict, List, Optional

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


def suggest_strategy(
    agent_history: List[Dict[str, Any]],
    available_strategies: List[str],
    model: str = "claude-sonnet-4-20250514",
) -> str:
    """Ask Claude which strategy to use based on agent history.

    Returns one of the available_strategies. Falls back to first strategy
    if the LLM call fails or anthropic is not installed.
    """
    if not HAS_ANTHROPIC:
        return available_strategies[0] if available_strategies else "explorer"

    history_summary = json.dumps(agent_history[-10:], indent=2)
    prompt = (
        f"Given the following experiment history for a hyperparameter search agent:\n"
        f"{history_summary}\n\n"
        f"Available strategies: {available_strategies}\n\n"
        f"Which strategy should the agent use next? Reply with ONLY the strategy name."
    )

    try:
        client = anthropic.Anthropic()
        message = client.messages.create(
            model=model,
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}],
        )
        suggestion = message.content[0].text.strip().lower()
        if suggestion in available_strategies:
            return suggestion
    except Exception:
        pass

    return available_strategies[0] if available_strategies else "explorer"
