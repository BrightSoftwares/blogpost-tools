"""Configuration loading, validation, and bootstrap for Internal Linking v2.

Spec: 951.123.AINOTE.solo.out.ainote-internal-linking-v2-spec.md
(Section 1 "Phase 0 — Bootstrap & Config Load" and Section 3
"Configuration Interface").

This module implements the full config schema (all fields documented in
the spec's ``internal-linking-config.yml`` example), because Phase 3-6
will reuse it unchanged. Only Phase 0-2 of the pipeline actually *read*
these values today (see ``internal_linking_v2.py``); fields such as
``max_links_per_post`` or ``distribution_strategy`` are validated and
carried in the returned config dict but are not consumed until the
scoring/insertion/migration/reporting phases are implemented.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Raised when configuration is missing required keys or has invalid values."""


VALID_LANGS = ("en", "fr", "es", "de", "it", "pt")
VALID_MODES = ("full", "migrate-only", "audit")
VALID_DISTRIBUTION_STRATEGIES = ("spread", "end-heavy", "uniform")
VALID_ANCHOR_TEXT_STRATEGIES = ("title-priority", "context", "filename")
REQUIRED_KEYS = ("posts_dir", "seo_dir", "lang")

# Mirrors the documented defaults in internal-linking-config.example.yml
# (spec Section 3). CLI flags and a user config file override these.
DEFAULT_CONFIG: Dict[str, Any] = {
    "posts_dir": None,
    "seo_dir": None,
    "lang": None,
    "mode": "full",
    "dry_run": False,
    "report_only": False,
    "skip_migration": False,
    "max_links_per_post": 8,
    "min_post_length_words": 300,
    "link_density_max": 0.05,
    "min_paragraphs_between_links": 3,
    "max_links_per_section": 1,
    "distribution_strategy": "spread",
    "anchor_text_strategy": "title-priority",
    "future_cutoff_date": "auto",
    "include_unpublished": False,
    "excluded_source_slugs": [],
    "keyword_min_length": 3,
    "keyword_min_ngram": 2,
    "keyword_max_ngram": 5,
    "log_level": "INFO",
    "log_file": None,
    "write_aliases_csv": True,
}


def load_yaml_config(config_path: str) -> Dict[str, Any]:
    """Load a YAML config file merged over ``DEFAULT_CONFIG``.

    If the file does not exist, logs a warning and returns the built-in
    defaults unchanged (callers typically still need ``posts_dir``,
    ``seo_dir``, and ``lang`` supplied via CLI overrides in that case).

    Args:
        config_path: Path to the YAML config file.

    Returns:
        Merged configuration dictionary (defaults <- YAML file).

    Raises:
        ConfigError: If the file exists but contains invalid YAML.
    """
    config = dict(DEFAULT_CONFIG)
    path = Path(config_path)

    if not path.is_file():
        logger.warning(f"Config file not found: {config_path}; using built-in defaults")
        return config

    try:
        with open(path, "r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML in config file {config_path}: {e}") from e

    if not isinstance(loaded, dict):
        raise ConfigError(f"Config file {config_path} must contain a YAML mapping")

    config.update(loaded)
    return config


def validate_config(cfg: Dict[str, Any]) -> None:
    """Validate a merged configuration dictionary (fail-fast).

    Args:
        cfg: Merged configuration (defaults <- YAML file <- CLI overrides).

    Raises:
        ConfigError: On any missing required key or invalid value.
    """
    for key in REQUIRED_KEYS:
        if not cfg.get(key):
            raise ConfigError(f"Missing required config: {key}")

    if cfg["lang"] not in VALID_LANGS:
        raise ConfigError(f"Unsupported lang: {cfg['lang']}")

    if cfg["mode"] not in VALID_MODES:
        raise ConfigError(f"Invalid mode: {cfg['mode']}")

    if cfg["distribution_strategy"] not in VALID_DISTRIBUTION_STRATEGIES:
        raise ConfigError(f"Invalid distribution_strategy: {cfg['distribution_strategy']}")

    if cfg["anchor_text_strategy"] not in VALID_ANCHOR_TEXT_STRATEGIES:
        raise ConfigError(f"Invalid anchor_text_strategy: {cfg['anchor_text_strategy']}")

    if not (1 <= cfg["max_links_per_post"] <= 50):
        raise ConfigError("max_links_per_post must be 1-50")

    if not (0.001 <= cfg["link_density_max"] <= 0.5):
        raise ConfigError("link_density_max must be 0.001-0.5")

    if not Path(cfg["posts_dir"]).is_dir():
        raise ConfigError(f"posts_dir does not exist: {cfg['posts_dir']}")


def parse_iso_date(value: str) -> date:
    """Parse a ``YYYY-MM-DD`` string into a ``date``.

    Args:
        value: ISO 8601 date string.

    Returns:
        Parsed date.

    Raises:
        ConfigError: If the string is not a valid ISO date.
    """
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError) as e:
        raise ConfigError(f"Invalid ISO date '{value}': {e}") from e


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Configure the root logger for console (and optionally file) output.

    Args:
        level: One of DEBUG, INFO, WARNING, ERROR, CRITICAL.
        log_file: Optional path to a rotating log file (3 MB x 3 backups).
    """
    handlers: list = [logging.StreamHandler()]

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(
            RotatingFileHandler(
                log_file,
                maxBytes=3 * 1024 * 1024,
                backupCount=3,
                encoding="utf-8",
            )
        )

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
        force=True,
    )


def bootstrap(config_path: str, cli_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Load, merge, validate, and finalize configuration (Phase 0).

    Args:
        config_path: Path to the YAML config file (may not exist).
        cli_overrides: CLI flag values to layer on top of the file/defaults.
            Keys with a value of None are ignored (not passed by the user).

    Returns:
        Finalized config dict. ``future_cutoff_date`` is resolved to a
        ``date`` object (either today UTC, if "auto", or the parsed
        explicit date).

    Raises:
        ConfigError: If validation fails.
    """
    cli_overrides = {k: v for k, v in (cli_overrides or {}).items() if v is not None}

    config = load_yaml_config(config_path)
    config.update(cli_overrides)
    validate_config(config)

    if config["future_cutoff_date"] == "auto":
        config["future_cutoff_date"] = datetime.utcnow().date()
    else:
        config["future_cutoff_date"] = parse_iso_date(config["future_cutoff_date"])

    setup_logging(level=config.get("log_level") or "INFO", log_file=config.get("log_file"))

    return config
