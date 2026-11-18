"""Phase 1 sanity check: is Odoo up, can we log in, are the modules + demo data there?

Standard library only, so it runs before the Python project exists:
    python3 scripts/check_odoo.py
"""

import sys
import xmlrpc.client

URL, DB, USER, PASSWORD = "http://localhost:8069", "odoo_demo", "admin", "admin"
MODULES = ["crm", "sale_management", "account"]

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
print("Server version:", common.version()["server_version"])

uid = common.authenticate(DB, USER, PASSWORD, {})
if not uid:
    sys.exit(f"Login failed for {USER!r} on database {DB!r}")
print(f"Logged in to {DB!r} as {USER!r} (uid={uid})")

models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")


def call(model, method, *args, **kwargs):
    return models.execute_kw(DB, uid, PASSWORD, model, method, list(args), kwargs)


for mod in call("ir.module.module", "search_read", [["name", "in", MODULES]],
                fields=["name", "state", "demo"]):
    print(f"  module {mod['name']:<16} state={mod['state']:<10} demo_data={mod['demo']}")

counts = {
    "CRM leads/opportunities": call("crm.lead", "search_count", []),
    "Sales orders": call("sale.order", "search_count", []),
    "Posted customer invoices": call(
        "account.move", "search_count",
        [["move_type", "=", "out_invoice"], ["state", "=", "posted"]]),
    "Partners": call("res.partner", "search_count", []),
}
for label, n in counts.items():
    print(f"  {label:<26} {n}")

if counts["CRM leads/opportunities"] == 0:
    sys.exit("No CRM records: demo data was NOT loaded.")
print("OK: Odoo is ready.")
