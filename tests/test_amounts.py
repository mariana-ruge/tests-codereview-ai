from decimal import Decimal
import pytest

from payments_svc.amounts import (
    AmountError,
    CurrencyError,
    MAX_AMOUNT,
    calculate_fee,
    normalize_currency,
    parse_amount,
    round_money,
    total_with_fee,
    validate_amount,
)


# === Tests para parse_amount ===

def test_parse_amount_valid_types():
    assert parse_amount(100) == Decimal("100")
    assert parse_amount(100.5) == Decimal("100.5")
    assert parse_amount("100.00") == Decimal("100.00")
    assert parse_amount("  100.00  ") == Decimal("100.00")
    assert parse_amount(Decimal("100.00")) == Decimal("100.00")


def test_parse_amount_none_raises_error():
    with pytest.raises(AmountError, match="amount is required"):
        parse_amount(None)


@pytest.mark.parametrize(
    "invalid_input",
    [
        "abc",
        "100a",
        "",
        "   ",
        [],
        {},
    ]
)
def test_parse_amount_non_numeric_raises_error(invalid_input):
    with pytest.raises(AmountError, match="amount must be numeric"):
        parse_amount(invalid_input)


@pytest.mark.parametrize(
    "infinite_input",
    [
        "Infinity",
        "-Infinity",
        "NaN",
    ]
)
def test_parse_amount_non_finite_raises_error(infinite_input):
    with pytest.raises(AmountError, match="amount must be finite"):
        parse_amount(infinite_input)


# === Tests para normalize_currency ===

@pytest.mark.parametrize(
    "raw_currency, expected",
    [
        ("usd", "USD"),
        ("eur", "EUR"),
        ("cop", "COP"),
        ("  usd  ", "USD"),
        ("USD", "USD"),
    ]
)
def test_normalize_currency_valid(raw_currency, expected):
    assert normalize_currency(raw_currency) == expected


@pytest.mark.parametrize(
    "invalid_currency, error_msg",
    [
        (None, "currency is required"),
        ("", "currency is required"),
        ("   ", "currency is required"),
    ]
)
def test_normalize_currency_missing_raises_error(invalid_currency, error_msg):
    with pytest.raises(CurrencyError, match=error_msg):
        normalize_currency(invalid_currency)


def test_normalize_currency_unsupported_raises_error():
    with pytest.raises(CurrencyError, match="unsupported currency: MXN"):
        normalize_currency("MXN")


# === Tests para validate_amount ===

def test_validate_amount_valid():
    # No debería levantar ninguna excepción
    validate_amount(Decimal("0"))
    validate_amount(Decimal("100.00"))
    validate_amount(MAX_AMOUNT)


def test_validate_amount_negative_raises_error():
    with pytest.raises(AmountError, match="amount cannot be negative"):
        validate_amount(Decimal("-0.01"))


def test_validate_amount_exceeds_max_raises_error():
    with pytest.raises(AmountError, match="amount exceeds maximum allowed"):
        validate_amount(MAX_AMOUNT + Decimal("0.01"))


# === Tests para round_money ===

@pytest.mark.parametrize(
    "value, expected",
    [
        (Decimal("10.004"), Decimal("10.00")),
        (Decimal("10.006"), Decimal("10.01")),
        # Comportamiento ROUND_HALF_EVEN (redondeo bancario)
        (Decimal("10.005"), Decimal("10.00")),  # el dígito anterior (0) es par
        (Decimal("10.015"), Decimal("10.02")),  # el dígito anterior (1) es impar, sube a 2 (par)
        (Decimal("10.025"), Decimal("10.02")),  # el dígito anterior (2) es par
    ]
)
def test_round_money(value, expected):
    assert round_money(value) == expected


# === Tests para calculate_fee ===

def test_calculate_fee_zero_amount():
    assert calculate_fee(Decimal("0.00"), "USD") == Decimal("0.00")
    assert calculate_fee(Decimal("0.00"), "EUR") == Decimal("0.00")
    assert calculate_fee(Decimal("0.00"), "COP") == Decimal("0.00")


@pytest.mark.parametrize(
    "amount, currency, expected_fee",
    [
        # USD: Rate 2.9%, Min 0.30
        (Decimal("5.00"), "USD", Decimal("0.30")),      # 5 * 0.029 = 0.145 < 0.30
        (Decimal("10.00"), "USD", Decimal("0.30")),     # 10 * 0.029 = 0.29 < 0.30
        (Decimal("11.00"), "USD", Decimal("0.32")),     # 11 * 0.029 = 0.319 (redondea a 0.32)
        (Decimal("100.00"), "USD", Decimal("2.90")),    # 100 * 0.029 = 2.90
        # EUR: Rate 2.5%, Min 0.25
        (Decimal("5.00"), "EUR", Decimal("0.25")),      # 5 * 0.025 = 0.125 < 0.25
        (Decimal("10.00"), "EUR", Decimal("0.25")),     # 10 * 0.025 = 0.25
        (Decimal("100.00"), "EUR", Decimal("2.50")),    # 100 * 0.025 = 2.50
        # COP: Rate 1.9%, Min 900.00
        (Decimal("1000.00"), "COP", Decimal("900.00")), # 1000 * 0.019 = 19 < 900
        (Decimal("10000.00"), "COP", Decimal("900.00")),# 10000 * 0.019 = 190 < 900
        (Decimal("50000.00"), "COP", Decimal("950.00")),# 50000 * 0.019 = 950 >= 900
    ]
)
def test_calculate_fee_valid(amount, currency, expected_fee):
    assert calculate_fee(amount, currency) == expected_fee


def test_calculate_fee_validates_inputs():
    # Debe propagar AmountError
    with pytest.raises(AmountError, match="amount cannot be negative"):
        calculate_fee(Decimal("-1.00"), "USD")

    # Debe propagar CurrencyError
    with pytest.raises(CurrencyError, match="unsupported currency: MXN"):
        calculate_fee(Decimal("100.00"), "MXN")


# === Tests para total_with_fee ===

@pytest.mark.parametrize(
    "amount, currency, expected_total",
    [
        (Decimal("0.00"), "USD", Decimal("0.00")),
        (Decimal("5.00"), "USD", Decimal("5.30")),      # 5.00 + 0.30 fee = 5.30
        (Decimal("100.00"), "USD", Decimal("102.90")),  # 100.00 + 2.90 fee = 102.90
        (Decimal("50000.00"), "COP", Decimal("50950.00")), # 50000 + 950 fee = 50950
    ]
)
def test_total_with_fee_valid(amount, currency, expected_total):
    assert total_with_fee(amount, currency) == expected_total


def test_total_with_fee_validates_inputs():
    with pytest.raises(AmountError, match="amount cannot be negative"):
        total_with_fee(Decimal("-1.00"), "USD")

    with pytest.raises(CurrencyError, match="unsupported currency: MXN"):
        total_with_fee(Decimal("100.00"), "MXN")
