# CI gate policy

## Purpose

The AI review gate turns local review practice into CI infrastructure for `payments-svc`.

In class 15 the gate runs on pull requests, reads only the PR diff, calls a real AI model through OpenRouter, validates the JSON verdict, and publishes the result in the GitHub Actions summary.

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

## Secrets and privacy

The API key must live in GitHub Secrets as `OPENROUTER_API_KEY`. It must never be committed, printed, echoed, or included in artifacts.

The workflow sends only the PR diff to the model. It does not send the full repository, remote history, unrelated files, or GitHub metadata that the model does not need.

## Class 15 boundary

This first version proves that the AI reviewer can run in GitHub Actions. It does not attempt full rollout governance yet.

Class 16 will introduce shadow mode and promotion criteria. Class 17 will add cost, latency, cache, and routing controls.
