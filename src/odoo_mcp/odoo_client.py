"""A small wrapper around Odoo's external XML-RPC API.

Odoo exposes two XML-RPC endpoints:
  /xmlrpc/2/common  -> version(), authenticate()          (no login needed)
  /xmlrpc/2/object  -> execute_kw(db, uid, password, model, method, args, kwargs)

Every model method (search_read, create, read_group, ...) goes through execute_kw.
This module turns low-level failures into three clear exception types so callers
(like the MCP tools) can show the user a useful message.
"""

import http.client
import xmlrpc.client
from typing import Any

from .config import Settings


class OdooError(Exception):
    """Any failure talking to Odoo (base class)."""


class OdooConnectionError(OdooError):
    """Odoo can't be reached: server down, wrong URL, or timeout."""


class OdooAuthError(OdooError):
    """Login rejected: wrong database, user or password."""


class OdooReadOnlyError(OdooError):
    """A write was attempted while ODOO_READ_ONLY is on."""


def _make_transport(url: str, timeout: float) -> xmlrpc.client.Transport:
    """Return the standard XML-RPC transport with a socket timeout added.

    xmlrpc.client has no timeout by default, so a hung Odoo would block forever.
    """
    base = xmlrpc.client.SafeTransport if url.startswith("https://") else xmlrpc.client.Transport

    class TimeoutTransport(base):
        def make_connection(self, host):
            conn = super().make_connection(host)
            conn.timeout = timeout  # applied when the socket connects
            return conn

    return TimeoutTransport()


def _fault_message(fault: xmlrpc.client.Fault) -> str:
    """Odoo puts a full server traceback in faultString; the last line is the useful part."""
    lines = [line for line in str(fault.faultString).splitlines() if line.strip()]
    return lines[-1].strip() if lines else f"Odoo fault {fault.faultCode}"


class OdooClient:
    def __init__(
        self,
        url: str,
        db: str,
        user: str,
        password: str,
        timeout: float = 10.0,
        read_only: bool = False,
    ):
        self.url = url.rstrip("/")
        self.db = db
        self.user = user
        self.password = password
        self.timeout = timeout
        self.read_only = read_only
        self._uid: int | None = None  # cached after the first successful login

    @classmethod
    def from_settings(cls, settings: Settings) -> "OdooClient":
        return cls(
            settings.url, settings.db, settings.user, settings.password,
            read_only=settings.read_only,
        )

    # -- plumbing -----------------------------------------------------------

    def _proxy(self, endpoint: str) -> xmlrpc.client.ServerProxy:
        # A fresh proxy per call: ServerProxy isn't thread-safe, and it's cheap to create.
        return xmlrpc.client.ServerProxy(
            f"{self.url}/xmlrpc/2/{endpoint}",
            transport=_make_transport(self.url, self.timeout),
            allow_none=True,
        )

    def _call(self, func, *args):
        """Run one XML-RPC call, translating failures into OdooError subclasses."""
        try:
            return func(*args)
        except xmlrpc.client.Fault as e:
            # Odoo raised an exception server-side (unknown field, access rights, ...).
            raise OdooError(_fault_message(e)) from e
        except xmlrpc.client.ProtocolError as e:
            raise OdooConnectionError(
                f"HTTP {e.errcode} from Odoo at {self.url}: {e.errmsg}"
            ) from e
        except (OSError, http.client.HTTPException) as e:
            # ConnectionRefusedError, TimeoutError, DNS failures, dropped connections...
            raise OdooConnectionError(f"Cannot reach Odoo at {self.url} ({e})") from e

    # -- public API ---------------------------------------------------------

    def authenticate(self) -> int:
        """Log in once and cache the user id (uid) for later calls."""
        if self._uid is None:
            common = self._proxy("common")
            try:
                uid = self._call(common.authenticate, self.db, self.user, self.password, {})
            except OdooConnectionError:
                raise
            except OdooError as e:  # server-side failure at login, e.g. unknown database
                raise OdooAuthError(
                    f"Login failed on database {self.db!r} (check ODOO_DB): {e}"
                ) from e
            if not uid:  # Odoo returns False (not an error) for bad credentials
                raise OdooAuthError(
                    f"Login failed for user {self.user!r} on database {self.db!r}. "
                    "Check ODOO_USER and ODOO_PASSWORD."
                )
            self._uid = uid
        return self._uid

    def execute_kw(
        self, model: str, method: str, args: list, kwargs: dict | None = None
    ) -> Any:
        """Call any model method, e.g. execute_kw("res.partner", "search_count", [[]])."""
        uid = self.authenticate()
        models = self._proxy("object")
        return self._call(
            models.execute_kw, self.db, uid, self.password, model, method, args, kwargs or {}
        )

    def search_read(
        self,
        model: str,
        domain: list | None = None,
        fields: list[str] | None = None,
        limit: int | None = None,
        order: str | None = None,
    ) -> list[dict]:
        """Search records matching an Odoo domain and return the requested fields."""
        kwargs: dict[str, Any] = {}
        if fields:
            kwargs["fields"] = fields
        if limit:
            kwargs["limit"] = limit
        if order:
            kwargs["order"] = order
        return self.execute_kw(model, "search_read", [domain or []], kwargs)

    def search_count(self, model: str, domain: list | None = None) -> int:
        """Count records matching a domain (ignores any limit)."""
        return self.execute_kw(model, "search_count", [domain or []])

    def read_group(
        self, model: str, domain: list, fields: list[str], groupby: list[str]
    ) -> list[dict]:
        """Aggregate records server-side, like SQL GROUP BY.

        fields uses Odoo's "field:agg" syntax, e.g. ["expected_revenue:sum"].
        lazy=False groups by all `groupby` fields at once and returns a `__count` key.
        """
        return self.execute_kw(model, "read_group", [domain, fields, groupby], {"lazy": False})

    def create(self, model: str, values: dict) -> int:
        """Create one record and return its id."""
        # Second line of defence: even if a write tool were registered by mistake,
        # the client itself refuses to write in read-only mode.
        if self.read_only:
            raise OdooReadOnlyError(
                f"Refusing to create a {model} record: ODOO_READ_ONLY is enabled."
            )
        return self.execute_kw(model, "create", [values])
