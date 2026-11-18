"""MCP tool tests with a fake Odoo client injected (no Odoo, no subprocess).

Two levels:
- call the tool functions directly (fast, checks domains and output shape);
- go through the real MCP protocol with the SDK's in-memory Client, to check
  what an LLM host would actually see (tool list, schemas, is_error results).
"""

import asyncio
import importlib
from unittest.mock import MagicMock

import pytest
from mcp import Client
from mcp.server.mcpserver.exceptions import ToolError

from odoo_mcp import server
from odoo_mcp.odoo_client import OdooAuthError, OdooConnectionError, OdooReadOnlyError


@pytest.fixture
def odoo(monkeypatch):
    """A MagicMock standing in for OdooClient, returned by server.get_client()."""
    fake = MagicMock(name="OdooClient")
    fake.search_count.return_value = 0
    fake.search_read.return_value = []
    monkeypatch.setattr(server, "get_client", lambda: fake)
    return fake


def mcp_call(name: str, arguments: dict | None = None):
    """Call a tool through the MCP protocol, like a host would."""
    async def run():
        async with Client(server.mcp) as client:
            return await client.call_tool(name, arguments or {})
    return asyncio.run(run())


def mcp_tools() -> dict:
    async def run():
        async with Client(server.mcp) as client:
            return (await client.list_tools()).tools
    return {tool.name: tool for tool in asyncio.run(run())}


# -- read tools: domains and output shape ------------------------------------------

def test_list_leads_filters_by_stage(odoo, raw_lead):
    odoo.search_count.return_value = 10
    odoo.search_read.return_value = [raw_lead]

    result = server.list_leads(stage="Prop", limit=2)

    assert result["total"] == 10
    assert result["leads"][0]["customer"] == "Yozio"
    model, domain = odoo.search_read.call_args.args[:2]
    assert (model, domain) == ("crm.lead", [["stage_id.name", "ilike", "Prop"]])
    assert odoo.search_read.call_args.kwargs["limit"] == 2


def test_list_leads_without_stage_has_empty_domain(odoo):
    server.list_leads()
    assert odoo.search_read.call_args.args[1] == []


def test_search_partners_matches_name_email_phone(odoo, raw_partner):
    odoo.search_read.return_value = [raw_partner]
    result = server.search_partners(query="wood")
    assert result["partners"][0]["country"] == "United States"
    domain = odoo.search_read.call_args.args[1]
    assert domain[:2] == ["|", "|"]
    assert {leaf[0] for leaf in domain[2:]} == {"name", "email", "phone"}


def test_search_partners_rejects_blank_query(odoo):
    with pytest.raises(ToolError, match="must not be empty"):
        server.search_partners(query="   ")
    odoo.search_read.assert_not_called()


def test_get_sales_orders_filters_by_state(odoo, raw_order):
    odoo.search_read.return_value = [raw_order]
    result = server.get_sales_orders(state="sale")
    assert result["orders"][0]["reference"] == "S00016"
    assert odoo.search_read.call_args.args[1] == [["state", "=", "sale"]]


def test_get_unpaid_invoices_domain(odoo, raw_invoice):
    odoo.search_read.return_value = [raw_invoice]
    result = server.get_unpaid_invoices()
    assert result["invoices"][0]["amount_due"] == 31750.0
    domain = odoo.search_read.call_args.args[1]
    assert ["move_type", "=", "out_invoice"] in domain
    assert ["payment_state", "in", ["not_paid", "partial"]] in domain


def test_pipeline_summary_groups_opportunities_by_stage(odoo, raw_pipeline_groups):
    odoo.read_group.return_value = raw_pipeline_groups
    result = server.pipeline_summary()
    assert result["total_count"] == 7
    model, domain, fields, groupby = odoo.read_group.call_args.args
    assert domain == [["type", "=", "opportunity"]]
    assert groupby == ["stage_id"]


# -- errors become ToolError -----------------------------------------------------

def test_unreachable_odoo_becomes_tool_error(odoo):
    odoo.search_count.side_effect = OdooConnectionError("Cannot reach Odoo at http://x")
    with pytest.raises(ToolError, match="Is Odoo running"):
        server.list_leads()


def test_auth_failure_becomes_tool_error(odoo):
    odoo.read_group.side_effect = OdooAuthError("Login failed for user 'admin'")
    with pytest.raises(ToolError, match="Login failed"):
        server.pipeline_summary()


# -- create_lead: preview / confirm ------------------------------------------------

def test_create_lead_preview_writes_nothing(odoo):
    result = server.create_lead(name="Desks", partner_name="Wood Corner", expected_revenue=500)
    assert result["status"] == "preview"
    assert result["would_create"]["values"] == {
        "name": "Desks",
        "partner_name": "Wood Corner",
        "email_from": False,
        "expected_revenue": 500,
    }
    odoo.create.assert_not_called()


def test_create_lead_confirm_creates_and_returns_record(odoo, raw_lead):
    odoo.create.return_value = 43
    odoo.search_read.return_value = [raw_lead]

    result = server.create_lead(name="Modernize old offices", confirm=True)

    assert result["status"] == "created"
    assert result["lead"]["id"] == 43
    model, values = odoo.create.call_args.args
    assert model == "crm.lead" and values["name"] == "Modernize old offices"


@pytest.mark.parametrize(
    "kwargs, message",
    [({"name": "  "}, "must not be empty"), ({"name": "X", "email": "nope"}, "email")],
)
def test_create_lead_validation(odoo, kwargs, message):
    with pytest.raises(ToolError, match=message):
        server.create_lead(confirm=True, **kwargs)
    odoo.create.assert_not_called()


def test_create_lead_read_only_client_becomes_tool_error(odoo):
    odoo.create.side_effect = OdooReadOnlyError("ODOO_READ_ONLY is enabled")
    with pytest.raises(ToolError, match="ODOO_READ_ONLY"):
        server.create_lead(name="X", confirm=True)


# -- through the MCP protocol --------------------------------------------------------

def test_tool_result_is_structured_json(odoo, raw_lead):
    odoo.search_count.return_value = 1
    odoo.search_read.return_value = [raw_lead]
    result = mcp_call("list_leads", {"limit": 1})
    assert result.is_error is False
    assert result.structured_content["leads"][0]["stage"] == "Proposition"


def test_tool_error_message_reaches_the_llm(odoo):
    odoo.search_count.side_effect = OdooConnectionError("Cannot reach Odoo at http://x")
    result = mcp_call("list_leads")
    assert result.is_error is True
    assert "Is Odoo running" in result.content[0].text


def test_unexpected_exception_text_is_hidden_from_the_llm(odoo):
    # Why we convert errors to ToolError: other exceptions' text never leaves the server.
    odoo.search_count.side_effect = RuntimeError("internal detail")
    result = mcp_call("list_leads")
    assert result.is_error is True
    assert "internal detail" not in result.content[0].text


def test_schema_exposes_limits_and_enums():
    tools = mcp_tools()
    orders = tools["get_sales_orders"].input_schema["properties"]
    assert orders["limit"]["maximum"] == 50
    assert orders["state"]["anyOf"][0]["enum"] == ["draft", "sent", "sale", "cancel"]
    assert tools["list_leads"].annotations.read_only_hint is True


def test_invalid_arguments_are_rejected_before_odoo_is_called(odoo):
    result = mcp_call("list_leads", {"limit": 500})
    assert result.is_error is True
    odoo.search_read.assert_not_called()


# -- ODOO_READ_ONLY decides which tools exist -------------------------------------------

def _reload_server(monkeypatch, read_only: str):
    monkeypatch.setenv("ODOO_READ_ONLY", read_only)
    importlib.reload(server)  # registration happens at import time


@pytest.fixture
def restore_server(monkeypatch):
    yield
    monkeypatch.undo()          # restore the original environment first...
    importlib.reload(server)    # ...then rebuild the normal server for other tests


def test_write_tool_registered_by_default(monkeypatch, restore_server):
    _reload_server(monkeypatch, "false")
    tools = mcp_tools()
    assert "create_lead" in tools
    assert tools["create_lead"].annotations.read_only_hint is False


def test_read_only_mode_hides_write_tools(monkeypatch, restore_server):
    _reload_server(monkeypatch, "true")
    tools = mcp_tools()
    assert "create_lead" not in tools
    assert len(tools) == 5
