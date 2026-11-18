"""The MCP server: exposes Odoo data as tools an LLM can call.

MCP in a nutshell:
- An MCP *server* (this file) advertises *tools*: functions with a name, a
  description and a JSON schema for their inputs.
- An MCP *host* (Claude Desktop, an IDE, the MCP Inspector) starts this server as
  a subprocess, asks for the tool list (`tools/list`) and shows it to the LLM.
- When the LLM decides to use a tool, the host sends `tools/call` with arguments,
  we run the function, and the host hands our result back to the model.

Run it with `uv run odoo-mcp` (normally a host does this for you).
"""

import logging
from contextlib import contextmanager
from typing import Annotated, Any, Literal

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import Field

from . import formatting as fmt
from .config import load_settings
from .odoo_client import OdooAuthError, OdooClient, OdooConnectionError, OdooError

# With the stdio transport, stdin/stdout carry the JSON-RPC messages between the
# host and this server, so never print() to stdout here: it would corrupt the stream.
# The SDK already sends logging output to stderr, so use a logger for diagnostics.
log = logging.getLogger("odoo_mcp")

# `instructions` is sent to the host when it connects: a short briefing on what
# this server is for. Many hosts add it to the LLM's context.
mcp = MCPServer(
    "odoo",
    instructions=(
        "Read-only access to an Odoo 18 ERP: CRM leads/opportunities, customers "
        "(partners), sales orders and unpaid customer invoices. Amounts are in the "
        "record's currency (company currency for CRM)."
    ),
)

# Tool annotations are hints for the host/LLM about a tool's behaviour. read_only_hint
# says "safe to call, changes nothing", so hosts may skip asking the user for approval.
READ_ONLY = ToolAnnotations(read_only_hint=True, open_world_hint=False)

# Type hints become the tool's JSON input schema. Annotated + Field adds a
# per-parameter description and constraints (here 1..50) that the LLM can see.
Limit = Annotated[int, Field(ge=1, le=50, description="Maximum number of records to return (1-50).")]

_client: OdooClient | None = None


def get_client() -> OdooClient:
    """Create the Odoo client on first use, so the server starts even if Odoo is down."""
    global _client
    if _client is None:
        try:
            _client = OdooClient.from_settings(load_settings())
        except ValueError as e:  # missing .env values
            raise ToolError(str(e)) from e
    return _client


@contextmanager
def odoo_errors():
    """Turn Odoo failures into ToolError.

    ToolError is the error whose message the LLM actually gets to read (the result
    comes back with is_error=True). In MCP SDK v2 the text of any *other* exception
    is hidden from the model, which then only sees "Error executing tool X" and
    can't tell the user what went wrong.
    """
    try:
        yield
    except OdooConnectionError as e:
        log.warning("Odoo unreachable: %s", e)
        raise ToolError(f"{e}. Is Odoo running? Try `docker compose up -d`.") from e
    except OdooAuthError as e:
        log.warning("Odoo login failed: %s", e)
        raise ToolError(str(e)) from e
    except OdooError as e:
        raise ToolError(f"Odoo returned an error: {e}") from e


# --- Tools -------------------------------------------------------------------
# @mcp.tool() registers a function as a tool. Its name becomes the tool name, its
# docstring becomes the description the LLM reads to decide *when* to call it,
# and its type hints become the input schema. The return value (a dict here) is
# sent back as JSON, both as text and as `structured_content`.


@mcp.tool(annotations=READ_ONLY)
def list_leads(
    stage: Annotated[
        str | None,
        Field(description="Filter by stage name, case-insensitive partial match "
                          "(e.g. 'New', 'Qualified', 'Proposition', 'Won'). Omit for all stages."),
    ] = None,
    limit: Limit = 10,
) -> dict[str, Any]:
    """List CRM leads and opportunities, highest expected revenue first.

    Use for questions like "what's in the pipeline?", "show deals in Proposition"
    or "who are our biggest prospects?". Each record has type "lead" (not yet
    qualified) or "opportunity" (in the sales pipeline). `total` is the number of
    matching records; `leads` holds at most `limit` of them.
    """
    domain = [["stage_id.name", "ilike", stage]] if stage else []
    with odoo_errors():
        client = get_client()
        total = client.search_count("crm.lead", domain)
        rows = client.search_read(
            "crm.lead", domain, fmt.LEAD_FIELDS, limit=limit, order="expected_revenue desc, id"
        )
    return {"total": total, "leads": [fmt.shape_lead(r) for r in rows]}


@mcp.tool(annotations=READ_ONLY)
def search_partners(
    query: Annotated[str, Field(description="Text to look for in the name, email or phone.")],
    limit: Limit = 10,
) -> dict[str, Any]:
    """Find customers and contacts (Odoo partners) by name, email or phone.

    Partners are companies or individual people; individuals may belong to a company.
    """
    if not query.strip():
        raise ToolError("query must not be empty.")
    domain = ["|", "|", ["name", "ilike", query], ["email", "ilike", query], ["phone", "ilike", query]]
    with odoo_errors():
        client = get_client()
        total = client.search_count("res.partner", domain)
        rows = client.search_read("res.partner", domain, fmt.PARTNER_FIELDS, limit=limit, order="name")
    return {"total": total, "partners": [fmt.shape_partner(r) for r in rows]}


@mcp.tool(annotations=READ_ONLY)
def get_sales_orders(
    # A Literal shows up in the schema as an enum, so the LLM can only pick valid values.
    state: Annotated[
        Literal["draft", "sent", "sale", "cancel"] | None,
        Field(description="draft = quotation, sent = quotation sent to customer, "
                          "sale = confirmed sales order, cancel = cancelled. Omit for all."),
    ] = None,
    limit: Limit = 10,
) -> dict[str, Any]:
    """List sales orders and quotations, newest first, with customer, total and invoice status."""
    domain = [["state", "=", state]] if state else []
    with odoo_errors():
        client = get_client()
        total = client.search_count("sale.order", domain)
        rows = client.search_read(
            "sale.order", domain, fmt.ORDER_FIELDS, limit=limit, order="date_order desc, id desc"
        )
    return {"total": total, "orders": [fmt.shape_order(r) for r in rows]}


@mcp.tool(annotations=READ_ONLY)
def get_unpaid_invoices(limit: Limit = 10) -> dict[str, Any]:
    """List posted customer invoices that are not (fully) paid, oldest due date first.

    Includes amount still due and days overdue. Use for "who owes us money?" or
    "which invoices are overdue?".
    """
    domain = [
        ["move_type", "=", "out_invoice"],
        ["state", "=", "posted"],
        ["payment_state", "in", ["not_paid", "partial"]],
    ]
    with odoo_errors():
        client = get_client()
        total = client.search_count("account.move", domain)
        rows = client.search_read(
            "account.move", domain, fmt.INVOICE_FIELDS, limit=limit, order="invoice_date_due, id"
        )
    return {"total": total, "invoices": [fmt.shape_invoice(r) for r in rows]}


@mcp.tool(annotations=READ_ONLY)
def pipeline_summary() -> dict[str, Any]:
    """Summarize the sales pipeline: number of opportunities and expected revenue per stage.

    weighted_revenue = expected revenue x win probability. Covers active
    opportunities only (not unqualified leads, not lost/archived deals).
    """
    with odoo_errors():
        groups = get_client().read_group(
            "crm.lead",
            [["type", "=", "opportunity"]],
            ["expected_revenue:sum", "prorated_revenue:sum"],
            ["stage_id"],
        )
    return fmt.shape_pipeline(groups)


def main() -> None:
    """Entry point for the `odoo-mcp` command."""
    mcp.run()  # default transport: stdio (talk to the host over stdin/stdout)


if __name__ == "__main__":
    main()
