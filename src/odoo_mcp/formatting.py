"""Turn raw Odoo records into small, LLM-friendly dicts.

Pure functions with no I/O, so they're easy to unit test. Why bother shaping?
Everything a tool returns goes into the LLM's context window, so we keep only
useful fields, resolve relations to names, and use JSON null instead of Odoo's False.
"""

from datetime import date
from typing import Any

# Fields requested from Odoo per model (fetch only what the shapers below use).
LEAD_FIELDS = [
    "name", "type", "stage_id", "partner_id", "partner_name", "contact_name",
    "email_from", "expected_revenue", "probability", "user_id", "date_deadline",
]
PARTNER_FIELDS = ["name", "is_company", "parent_id", "email", "phone", "city", "country_id"]
ORDER_FIELDS = [
    "name", "partner_id", "state", "date_order", "amount_total", "currency_id",
    "user_id", "invoice_status",
]
INVOICE_FIELDS = [
    "name", "partner_id", "invoice_date", "invoice_date_due", "amount_total",
    "amount_residual", "currency_id", "payment_state",
]


def m2o_name(value: Any) -> str | None:
    """Many2one fields arrive as [id, "Display Name"] (or False when empty). Keep the name."""
    return value[1] if value else None


def clean(value: Any) -> Any:
    """Odoo uses False for 'empty' on every field type; None (JSON null) is clearer."""
    return None if value is False else value


def shape_lead(r: dict) -> dict:
    return {
        "id": r["id"],
        "name": r["name"],
        "type": r["type"],  # "lead" (unqualified) or "opportunity" (in the pipeline)
        "stage": m2o_name(r["stage_id"]),
        # Many leads have no linked partner yet, only a typed-in company name.
        "customer": m2o_name(r["partner_id"]) or clean(r["partner_name"]),
        "contact": clean(r["contact_name"]),
        "email": clean(r["email_from"]),
        "expected_revenue": r["expected_revenue"],
        "probability": r["probability"],
        "salesperson": m2o_name(r["user_id"]),
        "deadline": clean(r["date_deadline"]),
    }


def shape_partner(r: dict) -> dict:
    return {
        "id": r["id"],
        "name": r["name"],
        "is_company": r["is_company"],
        "company": m2o_name(r["parent_id"]),  # employer, for individual contacts
        "email": clean(r["email"]),
        "phone": clean(r["phone"]),
        "city": clean(r["city"]),
        "country": m2o_name(r["country_id"]),
    }


def shape_order(r: dict) -> dict:
    return {
        "id": r["id"],
        "reference": r["name"],  # e.g. "S00012"
        "customer": m2o_name(r["partner_id"]),
        "state": r["state"],
        "date": r["date_order"],
        "amount_total": r["amount_total"],
        "currency": m2o_name(r["currency_id"]),
        "salesperson": m2o_name(r["user_id"]),
        "invoice_status": r["invoice_status"],
    }


def shape_invoice(r: dict, today: date | None = None) -> dict:
    today = today or date.today()
    due = clean(r["invoice_date_due"])
    days_overdue = (today - date.fromisoformat(due)).days if due else 0
    return {
        "id": r["id"],
        "number": r["name"],  # e.g. "INV/2026/00003"
        "customer": m2o_name(r["partner_id"]),
        "invoice_date": clean(r["invoice_date"]),
        "due_date": due,
        "days_overdue": max(days_overdue, 0),
        "amount_total": r["amount_total"],
        "amount_due": r["amount_residual"],
        "currency": m2o_name(r["currency_id"]),
        "payment_state": r["payment_state"],
    }


def shape_pipeline(groups: list[dict]) -> dict:
    """Shape read_group rows (grouped by stage_id, lazy=False) into a summary."""
    stages = [
        {
            "stage": m2o_name(g["stage_id"]) or "No stage",
            "count": g["__count"],
            "expected_revenue": round(g["expected_revenue"], 2),
            "weighted_revenue": round(g["prorated_revenue"], 2),  # revenue x probability
        }
        for g in groups
    ]
    return {
        "stages": stages,
        "total_count": sum(s["count"] for s in stages),
        "total_expected_revenue": round(sum(s["expected_revenue"] for s in stages), 2),
        "total_weighted_revenue": round(sum(s["weighted_revenue"] for s in stages), 2),
    }
