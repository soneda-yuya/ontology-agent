"""PostgreSQL connection provider.

Connections are opened per Unit of Work and always closed (NFR-U1-9). TLS is
expected to be enforced via the DSN (``sslmode=require`` or higher, SECURITY-01).
For higher load this is where a connection pool / retry decorator would be
added — the port interface is unaffected (NFR design: future extension point).
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import psycopg


class ConnectionProvider:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    @contextmanager
    def connection(self) -> Iterator[psycopg.Connection]:
        conn = psycopg.connect(self._dsn)
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def unit_of_work(self) -> Iterator[psycopg.Connection]:
        """A transactional scope: commit on success, rollback on error (SECURITY-15)."""
        with self.connection() as conn:
            with conn.transaction():
                yield conn
