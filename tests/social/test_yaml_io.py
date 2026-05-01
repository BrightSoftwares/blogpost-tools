"""Tests for yaml_io helpers."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "social"))

from yaml_io import load_yaml, save_yaml


def test_load_save_roundtrip(tmp_path: Path) -> None:
    data = {"slug": "test", "status": "draft", "tags": ["a", "b"]}
    p = tmp_path / "data.yml"
    save_yaml(data, p)
    loaded = load_yaml(p)
    assert loaded == data


def test_load_list(tmp_path: Path) -> None:
    data = [{"slug": "a"}, {"slug": "b"}]
    p = tmp_path / "list.yml"
    save_yaml(data, p)
    loaded = load_yaml(p)
    assert isinstance(loaded, list)
    assert len(loaded) == 2


def test_load_missing_file_returns_empty_list(tmp_path: Path) -> None:
    result = load_yaml(tmp_path / "nonexistent.yml")
    assert result == []


def test_save_creates_parent_dirs(tmp_path: Path) -> None:
    nested = tmp_path / "a" / "b" / "c.yml"
    save_yaml({"x": 1}, nested)
    assert nested.exists()
