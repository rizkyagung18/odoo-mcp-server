"""Shared fixtures: realistic raw Odoo records, as search_read returns them."""

import pytest


@pytest.fixture
def raw_lead():
    return {
        "id": 43,
        "name": "Modernize old offices",
        "type": "lead",
        "stage_id": [3, "Proposition"],
        "partner_id": False,           # no linked partner...
        "partner_name": "Yozio",       # ...only a typed-in company name
        "contact_name": "Franny Seiller",
        "email_from": "fseiller1@example.com",
        "expected_revenue": 99755.0,
        "probability": 20.0,
        "user_id": False,
        "date_deadline": "2026-12-02",
    }


@pytest.fixture
def raw_partner():
    return {
        "id": 9,
        "name": "Wood Corner",
        "is_company": True,
        "parent_id": False,
        "email": "info@woodcorner.example",
        "phone": "(623)-853-7197",
        "city": "Turlock",
        "country_id": [233, "United States"],
    }


@pytest.fixture
def raw_order():
    return {
        "id": 16,
        "name": "S00016",
        "partner_id": [10, "Gemini Furniture"],
        "state": "sale",
        "date_order": "2026-11-18 13:18:27",
        "amount_total": 1186.5,
        "currency_id": [1, "USD"],
        "user_id": [6, "Marc Demo"],
        "invoice_status": "no",
    }


@pytest.fixture
def raw_invoice():
    return {
        "id": 4,
        "name": "INV/2026/00004",
        "partner_id": [14, "Acme Corporation"],
        "invoice_date": "2026-11-03",
        "invoice_date_due": "2026-11-03",
        "amount_total": 31750.0,
        "amount_residual": 31750.0,
        "currency_id": [1, "USD"],
        "payment_state": "not_paid",
    }


@pytest.fixture
def raw_pipeline_groups():
    # read_group(..., groupby=["stage_id"], lazy=False) output
    return [
        {"stage_id": [1, "New"], "__count": 3, "expected_revenue": 104000.0,
         "prorated_revenue": 10400.0, "__domain": []},
        {"stage_id": [4, "Won"], "__count": 3, "expected_revenue": 23800.0,
         "prorated_revenue": 23800.0, "__domain": []},
        {"stage_id": False, "__count": 1, "expected_revenue": 500.0,
         "prorated_revenue": 50.0, "__domain": []},
    ]
