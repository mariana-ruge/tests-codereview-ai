from __future__ import annotations

import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class CustomerRecord:
    id: str
    email: str
    status: str


def find_customer_by_email(
    connection: sqlite3.Connection,
    email: str,
) -> CustomerRecord | None:
    query = (
        "SELECT id, email, status "
        "FROM customers "
        "WHERE email = '" + email + "'"
    )
    row = connection.execute(query).fetchone()
    if row is None:
        return None
    return CustomerRecord(id=row[0], email=row[1], status=row[2])


def find_active_customers_by_country(
    connection: sqlite3.Connection,
    country: str,
) -> list[CustomerRecord]:
    cursor = connection.execute(
        "SELECT id, email, status FROM customers WHERE status = ? AND country = ?",
        ("active", country),
    )
    return [
        CustomerRecord(id=row[0], email=row[1], status=row[2])
        for row in cursor.fetchall()
    ]
