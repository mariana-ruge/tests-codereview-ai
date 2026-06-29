# Mutation testing summary

## Scope

Mutation testing was run against:

```text
src/payments_svc/refunds.py
```

The test command used by Cosmic Ray was:

```powershell
python -m unittest tests.test_amounts tests.test_refunds -v
```

## Result

- Total jobs: 46
- Complete: 46 (100.00%)
- Surviving mutants: 8 (17.39%)

## Surviving mutants

### Actionable candidates

These survivors point to refund behavior that deserves a contract decision or stronger tests:

- `validate_refunded_amount`: changing `amount < Decimal("0")` to `amount is Decimal("0")` survived.
  - Risk: negative `already_refunded` values may not be explicitly covered.
  - Prompt lesson: ask the model to test non-negative accumulator fields separately from payment amounts.

- `request_refund`: changing `remaining <= Decimal("0")` to `remaining == Decimal("0")` survived.
  - Risk: over-refunded states where `already_refunded > original_amount` may not be covered.
  - Prompt lesson: ask the model to test impossible or inconsistent accumulated refund states.

- `assert_refundable`: changing `decision.reason or "refund rejected"` to `decision.reason and "refund rejected"` survived.
  - Risk: rejection errors without a reason may raise an empty or misleading message.
  - Prompt lesson: ask the model to cover fallback error messages, not only status changes.

### Non-actionable or low-value survivors

These survivors are not good reasons, by themselves, to add tests in this module:

- Changing `@dataclass(frozen=True)` to `frozen=False`.
  - This affects object mutability, but immutability is not currently a confirmed refund contract.

- Changing enum status comparison from `is` to `==`.
  - For `StrEnum`, this is usually behaviorally equivalent for the current contract.

- Changing `refund_amount == Decimal("0")` to `refund_amount <= Decimal("0")`.
  - Negative refund amounts are rejected earlier by `validate_amount`, so this mutant does not expose a new runtime behavior in the current flow.

## Prompt iteration

The prompt should gain a mutation-testing layer:

- classify each surviving mutant before proposing tests
- connect actionable mutants to confirmed contracts or failure modes
- reject equivalent or non-actionable mutants instead of writing tests only to improve the mutation score
- ask for a human decision when the mutant exposes an ambiguous business rule

This layer is the main input for the versioned prompt created after this mutation-testing run.
