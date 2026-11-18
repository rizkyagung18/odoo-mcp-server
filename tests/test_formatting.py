"""Output shaping: raw Odoo records -> compact, LLM-friendly dicts."""

from datetime import date

from odoo_mcp import formatting as fmt


def test_m2o_name():
    assert fmt.m2o_name([7, "Azure Interior"]) == "Azure Interior"
    assert fmt.m2o_name(False) is None


def test_clean_only_replaces_false():
    assert fmt.clean(False) is None
    assert fmt.clean(0) == 0  # a real zero must survive
    assert fmt.clean("") == ""
    assert fmt.clean("x") == "x"


def test_shape_lead_falls_back_to_typed_company_name(raw_lead):
    lead = fmt.shape_lead(raw_lead)
    assert lead == {
        "id": 43,
        "name": "Modernize old offices",
        "type": "lead",
        "stage": "Proposition",
        "customer": "Yozio",
        "contact": "Franny Seiller",
        "email": "fseiller1@example.com",
        "expected_revenue": 99755.0,
        "probability": 20.0,
        "salesperson": None,
        "deadline": "2026-12-02",
    }


def test_shape_lead_prefers_linked_partner(raw_lead):
    raw_lead["partner_id"] = [9, "Wood Corner"]
    assert fmt.shape_lead(raw_lead)["customer"] == "Wood Corner"


def test_shape_lead_requests_only_the_fields_it_uses(raw_lead):
    # Every field the shaper reads must be in LEAD_FIELDS, or search_read won't return it.
    trimmed = {k: v for k, v in raw_lead.items() if k in fmt.LEAD_FIELDS or k == "id"}
    assert fmt.shape_lead(trimmed) == fmt.shape_lead(raw_lead)


def test_shape_partner(raw_partner):
    assert fmt.shape_partner(raw_partner) == {
        "id": 9,
        "name": "Wood Corner",
        "is_company": True,
        "company": None,
        "email": "info@woodcorner.example",
        "phone": "(623)-853-7197",
        "city": "Turlock",
        "country": "United States",
    }


def test_shape_order(raw_order):
    order = fmt.shape_order(raw_order)
    assert order["reference"] == "S00016"
    assert order["customer"] == "Gemini Furniture"
    assert order["currency"] == "USD"
    assert order["salesperson"] == "Marc Demo"


def test_shape_invoice_counts_days_overdue(raw_invoice):
    invoice = fmt.shape_invoice(raw_invoice, today=date(2026, 11, 18))
    assert invoice["number"] == "INV/2026/00004"
    assert invoice["amount_due"] == 31750.0
    assert invoice["days_overdue"] == 15


def test_shape_invoice_not_yet_due(raw_invoice):
    assert fmt.shape_invoice(raw_invoice, today=date(2026, 11, 1))["days_overdue"] == 0


def test_shape_invoice_without_due_date(raw_invoice):
    raw_invoice["invoice_date_due"] = False
    invoice = fmt.shape_invoice(raw_invoice, today=date(2026, 11, 18))
    assert invoice["due_date"] is None
    assert invoice["days_overdue"] == 0


def test_shape_pipeline_totals(raw_pipeline_groups):
    summary = fmt.shape_pipeline(raw_pipeline_groups)
    assert [s["stage"] for s in summary["stages"]] == ["New", "Won", "No stage"]
    assert summary["total_count"] == 7
    assert summary["total_expected_revenue"] == 128300.0
    assert summary["total_weighted_revenue"] == 34250.0
    assert "__domain" not in summary["stages"][0]  # internal keys dropped
