"""Phase 2 connection check: print the 5 biggest CRM leads using OdooClient.

    uv run python scripts/show_leads.py
"""

import sys

from odoo_mcp.config import load_settings
from odoo_mcp.odoo_client import OdooClient, OdooError


def name_of(many2one) -> str:
    # Many2one fields come back as [id, "Display Name"], or False when empty.
    return many2one[1] if many2one else "-"


def main() -> None:
    client = OdooClient.from_settings(load_settings())
    try:
        leads = client.search_read(
            "crm.lead",
            domain=[],
            fields=["name", "stage_id", "partner_id", "expected_revenue"],
            limit=5,
            order="expected_revenue desc",
        )
    except OdooError as e:
        sys.exit(f"{type(e).__name__}: {e}")

    print(f"Connected to {client.db!r} at {client.url} as uid={client.authenticate()}\n")
    print(f"{'Lead':<38} {'Stage':<12} {'Customer':<24} {'Expected':>10}")
    print("-" * 87)
    for lead in leads:
        print(
            f"{lead['name'][:37]:<38} {name_of(lead['stage_id']):<12} "
            f"{name_of(lead['partner_id'])[:23]:<24} {lead['expected_revenue']:>10,.0f}"
        )


if __name__ == "__main__":
    main()
