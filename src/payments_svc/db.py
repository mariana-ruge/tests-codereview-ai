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
    row = connection.execute(
        "SELECT id, email, status FROM customers WHERE email = ?",
        (email,),
    ).fetchone()
    if row is None:
        return None
    return CustomerRecord(id=row[0], email=row[1], status=row[2])


def search_customers_by_email_fragment(
    connection: sqlite3.Connection,
    email_fragment: str,
) -> list[CustomerRecord]:
    cursor = connection.execute(
        "SELECT id, email, status FROM customers WHERE email LIKE ?",
        (f"%{email_fragment}%",),
    )
    return [
        CustomerRecord(id=row[0], email=row[1], status=row[2])
        for row in cursor.fetchall()
    ]


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


def search_customers_by_country_prefix(
    connection: sqlite3.Connection,
    country_prefix: str,
) -> list[CustomerRecord]:
    cursor = connection.execute(
        "SELECT id, email, status FROM customers WHERE country LIKE ?",
        (f"{country_prefix}%",),
    )
    return [
        CustomerRecord(id=row[0], email=row[1], status=row[2])
        for row in cursor.fetchall()
    ]


def count_customers_for_status(
    connection: sqlite3.Connection,
    status: str,
) -> int:
    allowed_statuses = {"active", "blocked", "pending"}
    if status not in allowed_statuses:
        raise ValueError("unsupported customer status")

    row = connection.execute(
        "SELECT COUNT(*) FROM customers WHERE status = ?",
        (status,),
    ).fetchone()
    return int(row[0])
