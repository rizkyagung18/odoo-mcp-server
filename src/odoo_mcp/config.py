"""Settings loaded from the project's .env file (or real environment variables)."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# src/odoo_mcp/config.py -> project root. We load .env by explicit path because
# MCP hosts like Claude Desktop start the server from a different working directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

REQUIRED = ("ODOO_URL", "ODOO_DB", "ODOO_USER", "ODOO_PASSWORD")


@dataclass(frozen=True)
class Settings:
    url: str
    db: str
    user: str
    password: str


def load_settings(env_file: Path | None = None) -> Settings:
    """Read settings. Variables already set in the environment win over .env values."""
    load_dotenv(env_file or PROJECT_ROOT / ".env", override=False)

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
    )
