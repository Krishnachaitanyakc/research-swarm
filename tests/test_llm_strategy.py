"""Tests for LLM strategy selection."""

import pytest
from unittest.mock import patch, MagicMock
from research_swarm.llm_strategy import suggest_strategy


def test_fallback_without_anthropic():
    with patch("research_swarm.llm_strategy.HAS_ANTHROPIC", False):
        result = suggest_strategy([], ["explorer", "exploiter"])
        assert result == "explorer"


def test_fallback_empty_strategies():
    with patch("research_swarm.llm_strategy.HAS_ANTHROPIC", False):
        result = suggest_strategy([], [])
        assert result == "explorer"


@patch("research_swarm.llm_strategy.HAS_ANTHROPIC", True)
@patch("research_swarm.llm_strategy.anthropic")
def test_suggest_strategy_with_mock(mock_anthropic):
    mock_client = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="exploiter")]
    mock_client.messages.create.return_value = mock_message

    result = suggest_strategy(
        [{"metric": 0.5, "params": {"lr": 0.001}}],
        ["explorer", "exploiter", "specialist"],
    )
    assert result == "exploiter"


@patch("research_swarm.llm_strategy.HAS_ANTHROPIC", True)
@patch("research_swarm.llm_strategy.anthropic")
def test_suggest_strategy_invalid_response(mock_anthropic):
    mock_client = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text="invalid_strategy")]
    mock_client.messages.create.return_value = mock_message

    result = suggest_strategy([], ["explorer", "exploiter"])
    assert result == "explorer"  # Falls back to first


@patch("research_swarm.llm_strategy.HAS_ANTHROPIC", True)
@patch("research_swarm.llm_strategy.anthropic")
def test_suggest_strategy_api_error(mock_anthropic):
    mock_client = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client
    mock_client.messages.create.side_effect = Exception("API error")

    result = suggest_strategy([], ["explorer", "exploiter"])
    assert result == "explorer"
