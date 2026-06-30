import unittest
from dataclasses import FrozenInstanceError
from decimal import Decimal

from payments_svc.amounts import AmountError
from payments_svc.refunds import (
    RefundDecision,
    RefundStatus,
    assert_refundable,
    calculate_remaining_refundable,
    request_refund,
)


class TestRefunds(unittest.TestCase):
    def test_calculate_remaining_refundable_subtracts_refunded_amount(self):
        remaining = calculate_remaining_refundable(
            original_amount=Decimal("100.00"),
            already_refunded=Decimal("25.00"),
        )

        self.assertEqual(remaining, Decimal("75.00"))

    def test_request_refund_approves_valid_refund(self):
        decision = request_refund(
            original_amount=Decimal("100.00"),
            refund_amount=Decimal("25.00"),
        )

        self.assertEqual(decision.status, RefundStatus.APPROVED)
        self.assertEqual(decision.amount, Decimal("25.00"))
        self.assertIsNone(decision.reason)

    def test_request_refund_approves_refund_equal_to_remaining_amount(self):
        decision = request_refund(
            original_amount=Decimal("100.00"),
            refund_amount=Decimal("70.00"),
            already_refunded=Decimal("30.00"),
        )

        self.assertEqual(decision.status, RefundStatus.APPROVED)
        self.assertEqual(decision.amount, Decimal("70.00"))
        self.assertIsNone(decision.reason)

    def test_request_refund_rejects_zero_refund(self):
        decision = request_refund(
            original_amount=Decimal("100.00"),
            refund_amount=Decimal("0.00"),
        )

        self.assertEqual(decision.status, RefundStatus.REJECTED)
        self.assertEqual(decision.amount, Decimal("0.00"))
        self.assertEqual(decision.reason, "refund amount must be greater than zero")

    def test_request_refund_rejects_fully_refunded_payment(self):
        decision = request_refund(
            original_amount=Decimal("100.00"),
            refund_amount=Decimal("10.00"),
            already_refunded=Decimal("100.00"),
        )

        self.assertEqual(decision.status, RefundStatus.REJECTED)
        self.assertEqual(decision.amount, Decimal("0.00"))
        self.assertEqual(decision.reason, "payment is already fully refunded")

    def test_assert_refundable_raises_for_rejected_refund(self):
        with self.assertRaises(AmountError):
            assert_refundable(Decimal("100.00"), Decimal("0.00"))

    def test_request_refund_with_negative_refund_amount_raises_amount_error(self):
        with self.assertRaises(AmountError):
            request_refund(
                original_amount=Decimal("100.00"),
                refund_amount=Decimal("-10.00"),
            )

    def test_calculate_remaining_refundable_with_negative_already_refunded_raises_amount_error(self):
        with self.assertRaises(AmountError):
            calculate_remaining_refundable(
                original_amount=Decimal("100.00"),
                already_refunded=Decimal("-10.00"),
            )

    def test_request_refund_rejects_when_already_refunded_exceeds_original_amount(self):
        decision = request_refund(
            original_amount=Decimal("100.00"),
            refund_amount=Decimal("10.00"),
            already_refunded=Decimal("110.00"),
        )

        self.assertEqual(decision.status, RefundStatus.REJECTED)
        self.assertEqual(decision.amount, Decimal("0.00"))
        self.assertEqual(decision.reason, "payment is already fully refunded")

    def test_request_refund_rejects_refund_amount_greater_than_remaining(self):
        decision = request_refund(
            original_amount=Decimal("100.00"),
            refund_amount=Decimal("80.00"),
            already_refunded=Decimal("30.00"),
        )

        self.assertEqual(decision.status, RefundStatus.REJECTED)
        self.assertEqual(decision.amount, Decimal("0.00"))
        self.assertEqual(decision.reason, "refund exceeds refundable amount")

    def test_assert_refundable_does_not_raise_for_valid_refund(self):
        assert_refundable(Decimal("100.00"), Decimal("50.00"))

    def test_assert_refundable_raises_with_specific_reason_on_rejection(self):
        with self.assertRaises(AmountError) as ctx:
            assert_refundable(Decimal("100.00"), Decimal("0.00"))

        self.assertEqual(str(ctx.exception), "refund amount must be greater than zero")

    def test_refund_decision_is_immutable(self):
        decision = RefundDecision(
            status=RefundStatus.APPROVED,
            amount=Decimal("10.00"),
        )

        with self.assertRaises(FrozenInstanceError):
            decision.amount = Decimal("20.00")

