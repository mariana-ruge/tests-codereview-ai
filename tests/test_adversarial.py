from __future__ import annotations

import sqlite3
import unittest

from payments_svc.db import (
    find_active_customers_by_country,
    find_customer_by_email,
    search_customers_by_country_prefix,
    search_customers_by_email_fragment,
)


class TestAdversarialInputs(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.execute(
            """
            CREATE TABLE customers (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                status TEXT NOT NULL,
                country TEXT NOT NULL
            )
            """
        )
        self.connection.executemany(
            "INSERT INTO customers (id, email, status, country) VALUES (?, ?, ?, ?)",
            [
                ("cus_001", "victim@example.com", "active", "CO"),
                ("cus_002", "admin@example.com", "blocked", "US"),
            ],
        )

    def tearDown(self) -> None:
        self.connection.close()

    def test_owasp_a03_sqli_tautology_payload_is_rejected(self) -> None:
        payload = "' OR '1'='1"

        result = find_customer_by_email(self.connection, payload)

        self.assertIsNone(result)

    def test_parameterized_country_lookup_resists_sqli_payload(self) -> None:
        payload = "' OR '1'='1"

        result = find_active_customers_by_country(self.connection, payload)

        self.assertEqual([], result)

    def test_email_fragment_search_treats_sqli_payload_as_literal_text(self) -> None:
        payload = "' OR '1'='1"

        result = search_customers_by_email_fragment(self.connection, payload)

        self.assertEqual([], result)

    def test_country_prefix_search_treats_sqli_payload_as_literal_text(self) -> None:
        payload = "' OR '1'='1"

        result = search_customers_by_country_prefix(self.connection, payload)

        self.assertEqual([], result)

    def test_control_character_email_does_not_match_existing_customer(self) -> None:
        payload = "victim@example.com\n"

        result = find_customer_by_email(self.connection, payload)

        self.assertIsNone(result)

    def test_long_email_does_not_match_unrelated_customer(self) -> None:
        payload = f"{'a' * 100}@example.com"

        result = find_customer_by_email(self.connection, payload)

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
