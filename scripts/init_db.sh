#!/usr/bin/env bash
# Create the `odoo_demo` database WITH demo data and install CRM, Sales and Invoicing.
#
# Uses the Odoo CLI inside a one-off container (more reliable than scripting the
# web database manager). A database created this way gets the admin user
# login "admin" / password "admin".
#
# Usage: ./scripts/init_db.sh            (run from the project root, stack must be up)
set -euo pipefail

DB_NAME="${1:-odoo_demo}"
MODULES="crm,sale_management,account"

cd "$(dirname "$0")/.."

echo "Creating database '${DB_NAME}' and installing: ${MODULES} (takes a few minutes)..."
# -d: database to create/use, -i: modules to install, --stop-after-init: exit when done.
# Demo data is loaded by default on Odoo 18 (only --without-demo exists to disable it).
docker compose run --rm odoo \
  odoo -d "${DB_NAME}" -i "${MODULES}" --stop-after-init

echo "Done. Open http://localhost:8069 and log in with admin / admin."
