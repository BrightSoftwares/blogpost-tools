"""Read/write helpers for YAML files used by the social publishing pipeline."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


def load_yaml(path: Path) -> list | dict:
    """Load a YAML file; return empty list if file is missing or empty."""
    if not path.exists():
        logger.info("YAML file not found, returning empty: %s", path)
        return []
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    return yaml.safe_load(text) or []


def save_yaml(data: list | dict, path: Path) -> None:
    """Write data to a YAML file, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    logger.debug("Wrote YAML to %s", path)
