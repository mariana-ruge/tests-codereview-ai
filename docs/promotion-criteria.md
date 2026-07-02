# AI review promotion criteria

## Purpose

Shadow mode lets the AI reviewer collect evidence before it gains power over pull requests.

The reviewer can move from observation to warning or blocking only when a rule has enough agreement with human judgment.

Class 15 answered: can the AI reviewer run inside GitHub Actions on a real pull request?

Class 16 answers the next question: should that reviewer be allowed to influence the merge decision?

The answer is: not immediately. First, every relevant AI verdict becomes a gate run: a small record that compares model judgment with human judgment.

The class 16 demo should still use a real pull request. The difference is the operating policy: the workflow keeps calling OpenRouter, but the PR is not blocked by model judgment while the team is calibrating rules.

Class 15 intentionally shows a high-confidence blocker: SQL string concatenation with user input. Class 16 uses that as the contrast case: a blocker can exist, but broad blocking power still needs rollout evidence by rule.

## What improves after class 15?

| Class 15 | Class 16 |
| --- | --- |
| AI review is connected to GitHub Actions. | AI review gets a rollout policy. |
| The model can publish a blocking PR comment. | The workflow leaves a reviewer-friendly shadow comment without blocking. |
| A valid verdict proves the integration works. | Gate runs show whether rules deserve trust. |
| The demo asks if the reviewer runs. | The demo asks when a reviewer should influence merges. |

## What is a gate run?

A gate run is one reviewed case from the rollout period.

Each entry in `samples/ci/gate-runs.json` captures:

- the PR or scenario reviewed
- the rule being evaluated
- the action suggested by the AI
- the action a human reviewer would choose
- the lesson from the disagreement or agreement

This turns the class 15 PR comment into measurable evidence. Instead of asking "did the model sound convincing?", the team asks "does this rule agree with humans often enough to warn or block?"

## Rollout stages

| Stage | CI behavior | PR behavior | When to use |
| --- | --- | --- | --- |
| `shadow` | Runs and records results. | Does not comment or block. | New or uncalibrated rules. |
| `warn` | Runs and records results. | May comment with reviewer-friendly evidence. | Useful findings with tolerable false positives. |
| `block` | Fails the check for selected findings. | Prevents merge until fixed or overridden. | Stable, high-severity rules with strong agreement. |

## Promotion thresholds

| Promotion | Minimum evidence | Agreement | False positives | False negatives |
| --- | --- | --- | --- | --- |
| `shadow` to `warn` | 5 reviewed cases | At least 70% | At most 25% | Tracked, not blocking |
| `warn` to `block` | 10 reviewed cases | At least 90% | At most 5% | At most 10% |

## Initial candidates

| Rule | Current stage | Next step |
| --- | --- | --- |
| `security-sql-injection` | `shadow` | Candidate for `block` after more matching cases. |
| `payment-idempotency` | `shadow` | Candidate for `warn`; needs more cases to reduce false negatives. |
| `tests-missing-critical-path` | `shadow` | Keep observing; false positives are still too likely. |

## Override rule

Any blocking rule must have a documented human override path. An override is not a failure of the process; it becomes labeled data for the next calibration pass.
