"""OdooClient tests with XML-RPC mocked out: no Odoo needed."""

import xmlrpc.client
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from odoo_mcp.odoo_client import (
    OdooAuthError,
    OdooClient,
    OdooConnectionError,
    OdooError,
    OdooReadOnlyError,
    _make_transport,
)

DB, USER, PASSWORD = "odoo_demo", "admin", "secret"
TRACEBACK = (
    "Traceback (most recent call last):\n"
    '  File "/usr/lib/python3/dist-packages/odoo/models.py", line 1, in search_read\n'
    "ValueError: Invalid field 'nope' on model 'crm.lead'\n"
)


@pytest.fixture
def proxies(monkeypatch):
    """Replace ServerProxy with mocks: one for /common, one for /object."""
    common, obj = MagicMock(name="common"), MagicMock(name="object")
    common.authenticate.return_value = 7

    def fake_server_proxy(url, **kwargs):
        return common if url.endswith("/xmlrpc/2/common") else obj

    monkeypatch.setattr(xmlrpc.client, "ServerProxy", fake_server_proxy)
    return SimpleNamespace(common=common, object=obj)


@pytest.fixture
def client(proxies):
    return OdooClient("http://odoo.test:8069/", DB, USER, PASSWORD)


# -- authentication -------------------------------------------------------------

def test_authenticate_returns_and_caches_uid(client, proxies):
    assert client.authenticate() == 7
    assert client.authenticate() == 7
    proxies.common.authenticate.assert_called_once_with(DB, USER, PASSWORD, {})


def test_bad_credentials_raise_auth_error(client, proxies):
    proxies.common.authenticate.return_value = False  # what Odoo does on wrong password
    with pytest.raises(OdooAuthError, match="Login failed for user 'admin'"):
        client.authenticate()


def test_unknown_database_raises_auth_error(client, proxies):
    proxies.common.authenticate.side_effect = xmlrpc.client.Fault(
        1, 'Traceback...\npsycopg2.OperationalError: database "nope" does not exist'
    )
    with pytest.raises(OdooAuthError, match="check ODOO_DB") as exc:
        client.authenticate()
    assert "Traceback" not in str(exc.value)


# -- connection failures ----------------------------------------------------------

@pytest.mark.parametrize(
    "error",
    [ConnectionRefusedError(61, "Connection refused"), TimeoutError("timed out")],
)
def test_network_errors_raise_connection_error(client, proxies, error):
    proxies.common.authenticate.side_effect = error
    with pytest.raises(OdooConnectionError, match=r"Cannot reach Odoo at http://odoo\.test:8069"):
        client.search_read("crm.lead")


def test_http_error_raises_connection_error(client, proxies):
    proxies.common.authenticate.side_effect = xmlrpc.client.ProtocolError(
        "odoo.test/xmlrpc/2/common", 502, "Bad Gateway", {}
    )
    with pytest.raises(OdooConnectionError, match="HTTP 502"):
        client.authenticate()


# -- model calls ------------------------------------------------------------------

def test_search_read_builds_execute_kw_call(client, proxies):
    proxies.object.execute_kw.return_value = [{"id": 1, "name": "Lead"}]

    rows = client.search_read(
        "crm.lead", [["type", "=", "lead"]], ["name"], limit=5, order="id desc"
    )

    assert rows == [{"id": 1, "name": "Lead"}]
    proxies.object.execute_kw.assert_called_once_with(
        DB, 7, PASSWORD, "crm.lead", "search_read",
        [[["type", "=", "lead"]]],
        {"fields": ["name"], "limit": 5, "order": "id desc"},
    )


def test_search_read_omits_unset_options(client, proxies):
    client.search_read("res.partner")
    args = proxies.object.execute_kw.call_args.args
    assert args[5:] == ([[]], {})  # empty domain, no kwargs


def test_search_count(client, proxies):
    proxies.object.execute_kw.return_value = 39
    assert client.search_count("crm.lead") == 39
    assert proxies.object.execute_kw.call_args.args[3:5] == ("crm.lead", "search_count")


def test_read_group_is_not_lazy(client, proxies):
    client.read_group("crm.lead", [], ["expected_revenue:sum"], ["stage_id"])
    args = proxies.object.execute_kw.call_args.args
    assert args[4:] == ("read_group", [[], ["expected_revenue:sum"], ["stage_id"]], {"lazy": False})


def test_server_fault_is_trimmed_to_last_line(client, proxies):
    proxies.object.execute_kw.side_effect = xmlrpc.client.Fault(1, TRACEBACK)
    with pytest.raises(OdooError) as exc:
        client.search_read("crm.lead", fields=["nope"])
    assert str(exc.value) == "ValueError: Invalid field 'nope' on model 'crm.lead'"


def test_create_returns_new_id(client, proxies):
    proxies.object.execute_kw.return_value = 45
    assert client.create("crm.lead", {"name": "New"}) == 45
    assert proxies.object.execute_kw.call_args.args[4:] == ("create", [{"name": "New"}], {})


def test_create_refused_in_read_only_mode(proxies):
    client = OdooClient("http://odoo.test:8069", DB, USER, PASSWORD, read_only=True)
    with pytest.raises(OdooReadOnlyError):
        client.create("crm.lead", {"name": "New"})
    proxies.object.execute_kw.assert_not_called()  # never reached Odoo


# -- transport ----------------------------------------------------------------------

def test_transport_applies_timeout():
    conn = _make_transport("http://odoo.test:8069", timeout=3).make_connection("odoo.test:8069")
    assert conn.timeout == 3


def test_https_url_uses_safe_transport():
    assert isinstance(_make_transport("https://odoo.example.com", 5), xmlrpc.client.SafeTransport)
    assert not isinstance(_make_transport("http://odoo.test", 5), xmlrpc.client.SafeTransport)
