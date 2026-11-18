"""Optional integration tests against a real Odoo (read-only: nothing is written).

They run only when .env is configured and Odoo answers at ODOO_URL; otherwise
they're skipped. Run just these with:  uv run pytest -m integration -v
"""

import socket
from urllib.parse import urlparse

import pytest

from odoo_mcp import server
from odoo_mcp.config import load_settings
from odoo_mcp.odoo_client import OdooClient


def _odoo_settings():
    try:
        settings = load_settings()
    except ValueError:
        return None
    url = urlparse(settings.url)
    try:
        with socket.create_connection((url.hostname, url.port or 80), timeout=1):
            return settings
    except OSError:
        return None


SETTINGS = _odoo_settings()

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(SETTINGS is None, reason="Odoo not reachable or .env not configured"),
]


@pytest.fixture(scope="module")
def client():
    return OdooClient.from_settings(SETTINGS)


def test_login(client):
    assert isinstance(client.authenticate(), int)


def test_list_leads_against_demo_data(monkeypatch, client):
    monkeypatch.setattr(server, "get_client", lambda: client)
    result = server.list_leads(limit=3)
    assert result["total"] >= len(result["leads"]) > 0
    assert set(result["leads"][0]) >= {"name", "stage", "customer", "expected_revenue"}


def test_pipeline_summary_against_demo_data(monkeypatch, client):
    monkeypatch.setattr(server, "get_client", lambda: client)
    summary = server.pipeline_summary()
    assert summary["total_count"] > 0
    assert summary["total_expected_revenue"] > 0
