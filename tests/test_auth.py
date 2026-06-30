import unittest
from dataclasses import FrozenInstanceError

from payments_svc.auth import Role, User, can_refund, require_authenticated


class TestAuth(unittest.TestCase):
    def test_require_authenticated_returns_user(self):
        user = User(id="usr_1", role=Role.CUSTOMER, account_id="acct_1")

        self.assertIs(require_authenticated(user), user)

    def test_require_authenticated_rejects_missing_user(self):
        with self.assertRaises(PermissionError) as ctx:
            require_authenticated(None)

        self.assertEqual(str(ctx.exception), "authentication required")

    def test_support_can_refund_any_account(self):
        user = User(id="usr_1", role=Role.SUPPORT, account_id="acct_support")

        self.assertTrue(can_refund(user, "acct_customer"))

    def test_admin_can_refund_any_account(self):
        user = User(id="usr_1", role=Role.ADMIN, account_id="acct_admin")

        self.assertTrue(can_refund(user, "acct_customer"))

    def test_customer_can_refund_own_account(self):
        user = User(id="usr_1", role=Role.CUSTOMER, account_id="acct_1")

        self.assertTrue(can_refund(user, "acct_1"))

    def test_customer_cannot_refund_other_account(self):
        user = User(id="usr_1", role=Role.CUSTOMER, account_id="acct_1")

        self.assertFalse(can_refund(user, "acct_2"))

    def test_user_is_immutable(self):
        user = User(id="usr_1", role=Role.CUSTOMER, account_id="acct_1")

        with self.assertRaises(FrozenInstanceError):
            user.account_id = "acct_2"
