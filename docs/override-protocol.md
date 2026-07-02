# AI review override protocol

## Purpose

An override is a human decision that disagrees with the AI review result.

Overrides are not failures of the process. They are labeled data that helps improve the next version of the reviewer.

## What to capture

Each override should become one entry in `samples/ci/review-history.json`:

- PR or scenario reviewed
- route selected by the gate
- model used
- rule or category involved
- action requested by the model
- action chosen by the human reviewer
- outcome: agreement, false_positive, or false_negative
- lesson learned
- improvement to prompt, policy, routing, or model choice

## How this improves the reviewer

The model does not learn automatically from the file.

The team uses the file to make safer changes:

- adjust the prompt when the model misses a recurring risk
- keep a noisy rule in shadow instead of blocking PRs
- route sensitive changes to a stronger model
- add regression cases before changing model or policy
- promote only rules that agree with human reviewers over time

## Override examples

| Situation | Human action | Improvement |
| --- | --- | --- |
| Model blocks a missing-test finding that should only warn. | Change `block` to `warn`. | Clarify policy: missing tests block only for money movement or security-critical paths. |
| Model passes a risky refund edge case. | Change `pass` to `block`. | Add a refund-specific instruction and keep refunds on the strong route. |
| Model reports noise on docs-only changes. | Change `warn` to `pass`. | Keep docs-only route separate and ask for no findings unless docs change operational behavior. |

## Rule of thumb

Every override must answer one question:

What should we change so the next reviewer behaves closer to the human decision?
