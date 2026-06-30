import unittest

from fastapi import HTTPException

from payments_svc.api import (
    PaymentRequest,
    RefundRequest,
    create_payment,
    create_refund,
    health,
)


class TestApi(unittest.TestCase):
    def test_health_returns_ok(self):
        self.assertEqual(health(), {"status": "ok"})

    def test_create_payment_returns_amount_fee_and_total(self):
        response = create_payment(
            PaymentRequest(amount="100.00", currency="usd"),
        )

        self.assertEqual(response.amount, "100.00")
        self.assertEqual(response.currency, "USD")
        self.assertEqual(response.fee, "2.90")
        self.assertEqual(response.total, "102.90")

    def test_create_payment_rejects_invalid_amount(self):
        with self.assertRaises(HTTPException) as ctx:
            create_payment(PaymentRequest(amount="not-money", currency="USD"))

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertEqual(ctx.exception.detail, "amount must be numeric")

    def test_create_payment_rejects_unsupported_currency(self):
        with self.assertRaises(HTTPException) as ctx:
            create_payment(PaymentRequest(amount="10.00", currency="XYZ"))

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertEqual(ctx.exception.detail, "unsupported currency: XYZ")

    def test_create_refund_returns_approved_refund(self):
        response = create_refund(
            RefundRequest(
                original_amount="100.00",
                refund_amount="25.00",
                already_refunded="10.00",
            )
        )

        self.assertEqual(response.status, "approved")
        self.assertEqual(response.amount, "25.00")
        self.assertIsNone(response.reason)

    def test_create_refund_rejects_refund_exceeding_remaining_amount(self):
        with self.assertRaises(HTTPException) as ctx:
            create_refund(
                RefundRequest(
                    original_amount="100.00",
                    refund_amount="80.00",
                    already_refunded="30.00",
                )
            )

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertEqual(ctx.exception.detail, "refund exceeds refundable amount")

    def test_create_refund_rejects_invalid_decimal_input(self):
        with self.assertRaises(HTTPException) as ctx:
            create_refund(
                RefundRequest(
                    original_amount="100.00",
                    refund_amount="not-money",
                    already_refunded="0.00",
                )
            )

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertEqual(ctx.exception.detail, "amount must be numeric")
