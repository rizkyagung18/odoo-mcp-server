"""Settings loaded from the project's .env file (or real environment variables)."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# src/odoo_mcp/config.py -> project root. We load .env by explicit path because
# MCP hosts like Claude Desktop start the server from a different working directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

REQUIRED = ("ODOO_URL", "ODOO_DB", "ODOO_USER", "ODOO_PASSWORD")
TRUTHY = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    url: str
    db: str
    user: str
    password: str
    read_only: bool = False


def _load_env(env_file: Path | None = None) -> None:
    # override=False: variables already set in the environment win over .env values.
    load_dotenv(env_file or PROJECT_ROOT / ".env", override=False)


def read_only_mode() -> bool:
    """True when ODOO_READ_ONLY is truthy: all write tools are then disabled.

    Doesn't need the other settings, so the server can decide which tools to
    register at startup even if the Odoo credentials are missing.
    """
    _load_env()
    return os.environ.get("ODOO_READ_ONLY", "false").strip().lower() in TRUTHY


def load_settings(env_file: Path | None = None) -> Settings:
    """Read all settings, raising ValueError if a required one is missing."""
    _load_env(env_file)

    missing = [name for name in REQUIRED if not os.environ.get(name)]
    if missing:
        raise ValueError(
            f"Missing settings: {', '.join(missing)}. "
            "Copy .env.example to .env and fill them in."
        )

    return Settings(
        url=os.environ["ODOO_URL"].rstrip("/"),
        db=os.environ["ODOO_DB"],
        user=os.environ["ODOO_USER"],
        password=os.environ["ODOO_PASSWORD"],
        read_only=read_only_mode(),
    )
