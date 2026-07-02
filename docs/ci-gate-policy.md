# CI gate policy

## Purpose

The AI review gate turns local review practice into CI infrastructure for `payments-svc`.

In class 15 the gate runs on pull requests, reads only the PR diff, calls a real AI model through OpenRouter, validates the JSON verdict, and publishes the result in the GitHub Actions summary.

In class 16 the gate moves to shadow mode. It still validates the model output, but model decisions do not block the PR while the team measures agreement against human judgment.

This improves class 15 by adding governance. The AI reviewer is no longer just a visible PR comment; it becomes a system that can be measured before it is trusted.

The class 16 demo still runs through a real pull request. The visible change is policy: GitHub Actions still executes the AI reviewer, but model decisions stay in shadow until there is enough evidence to promote a rule.

## Inputs

- Pull request diff against `develop`.
- Versioned prompt: `prompts/ci-review.md`.
- Versioned JSON contract: `schemas/ai-review.schema.json`.
- GitHub secret: `OPENROUTER_API_KEY`.
- Optional model variable: `OPENROUTER_MODEL`.

## Actions

| Action | Meaning | Initial policy |
| --- | --- | --- |
| `block` | The check fails and the PR should not merge yet. | Only high-confidence, high-severity findings supported directly by the diff. |
| `warn` | The check passes, but the PR summary shows the concern. | Relevant findings that need human attention but are not safe to block yet. |
| `report` | The check passes and the finding is kept as calibration data. | Low-confidence observations or categories not calibrated yet. |
| `pass` | No findings. | The PR can proceed normally. |

## Shadow mode

Shadow mode separates infrastructure failures from model judgment:

- invalid JSON or a broken workflow still fails CI
- a model verdict of `block` is recorded but does not fail CI
- the workflow publishes evidence in the job summary and leaves a reviewer-friendly PR comment
- promotion to `warn` or `block` depends on measured agreement, not on a single impressive finding

The rollout dataset lives in `samples/ci/gate-runs.json`. It is intentionally small for the class demo, but it models the production habit: collect verdicts, compare them with human review, then promote only the rules that earn trust.

## Secrets and privacy

The API key must live in GitHub Secrets as `OPENROUTER_API_KEY`. It must never be committed, printed, echoed, or included in artifacts.

The workflow sends only the PR diff to the model. It does not send the full repository, remote history, unrelated files, or GitHub metadata that the model does not need.

## Class 15 boundary

This first version proves that the AI reviewer can run in GitHub Actions. It does not attempt full rollout governance yet.

Class 16 will introduce shadow mode and promotion criteria. Class 17 will add cost, latency, cache, and routing controls.
