import unittest
from decimal import Decimal

from payments_svc.amounts import AmountError
from payments_svc.refunds import (
    RefundStatus,
    assert_refundable,
    calculate_remaining_refundable,
    request_refund,
)


class TestRefundsIngenuo(unittest.TestCase):
    def test_calculate_remaining_refundable(self):
        remaining = calculate_remaining_refundable(
            original_amount=Decimal("100.00"),
            already_refunded=Decimal("25.00"),
        )

        self.assertEqual(remaining, Decimal("75.00"))

    def test_request_refund_approves_refund(self):
        decision = request_refund(
            original_amount=Decimal("100.00"),
            refund_amount=Decimal("25.00"),
        )

        self.assertEqual(decision.status, RefundStatus.APPROVED)
        self.assertEqual(decision.amount, Decimal("25.00"))

    def test_request_refund_rejects_when_fully_refunded(self):
        decision = request_refund(
            original_amount=Decimal("100.00"),
            refund_amount=Decimal("10.00"),
            already_refunded=Decimal("100.00"),
        )

        self.assertEqual(decision.status, RefundStatus.REJECTED)

    def test_assert_refundable_raises_for_invalid_refund(self):
        with self.assertRaises(AmountError):
            assert_refundable(
                original_amount=Decimal("100.00"),
                refund_amount=Decimal("0.00"),
            )
