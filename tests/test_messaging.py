"""Tests for agent communication (message queue)."""

import os
import tempfile
import pytest
from research_swarm.results import SharedResultStore


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_save_message(temp_dir):
    store = SharedResultStore(temp_dir)
    store.save_message("agent-1", "agent-2", "found good params")
    messages = store.get_messages("agent-2")
    assert len(messages) == 1
    assert messages[0]["from"] == "agent-1"
    assert messages[0]["content"] == "found good params"


def test_get_messages_empty(temp_dir):
    store = SharedResultStore(temp_dir)
    assert store.get_messages("agent-1") == []


def test_multiple_messages(temp_dir):
    store = SharedResultStore(temp_dir)
    store.save_message("agent-1", "agent-2", "msg1")
    store.save_message("agent-3", "agent-2", "msg2")
    messages = store.get_messages("agent-2")
    assert len(messages) == 2
    assert messages[0]["from"] == "agent-1"
    assert messages[1]["from"] == "agent-3"


def test_clear_messages(temp_dir):
    store = SharedResultStore(temp_dir)
    store.save_message("agent-1", "agent-2", "test")
    store.clear_messages("agent-2")
    assert store.get_messages("agent-2") == []


def test_message_has_timestamp(temp_dir):
    store = SharedResultStore(temp_dir)
    store.save_message("agent-1", "agent-2", "hello")
    messages = store.get_messages("agent-2")
    assert "timestamp" in messages[0]
    assert isinstance(messages[0]["timestamp"], float)


def test_messages_isolated_per_agent(temp_dir):
    store = SharedResultStore(temp_dir)
    store.save_message("agent-1", "agent-2", "for agent-2")
    store.save_message("agent-1", "agent-3", "for agent-3")
    assert len(store.get_messages("agent-2")) == 1
    assert len(store.get_messages("agent-3")) == 1
    assert store.get_messages("agent-2")[0]["content"] == "for agent-2"
