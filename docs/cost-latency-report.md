# AI review cost and latency report

## Purpose

Class 17 adds an operational planning step before the AI reviewer calls OpenRouter.

The goal is not to make the reviewer smarter. The goal is to make it sustainable in CI: choose the right model, leave a cache key, explain the route, and keep the latency target visible.

The plan records both the selected model and the source used to resolve it. In the PR comment, `OPENROUTER_MODEL_FAST` or `OPENROUTER_MODEL_STRONG` means the workflow used the GitHub variable; `default:...` means it fell back to the repository default.

## Routes

| Route | Model | When it applies | Latency target | Estimated cost |
| --- | --- | --- | --- | --- |
| `docs-only` | `OPENROUTER_MODEL_FAST` | Only docs or Markdown changed. | 30s | low |
| `fast` | `OPENROUTER_MODEL_FAST` | Small non-sensitive diffs. | 45s | low |
| `security-sensitive` | `OPENROUTER_MODEL_STRONG` | Security-sensitive paths such as `db.py`, auth, LLM support, or Semgrep rules. | 90s | medium |
| `payments-critical` | `OPENROUTER_MODEL_STRONG` | Money, refunds, or payment API behavior changed. | 90s | medium |
| `large-diff` | `OPENROUTER_MODEL_STRONG` | More than 120 added lines. | 120s | medium |

## Cache policy

Class 17 records a deterministic cache key from the PR diff.

For the video, cache is `report-only`: the workflow does not skip the model call yet. That keeps the demo honest while making the next optimization visible.

## Why this improves the gate

Class 15 proved the gate can block.

Class 16 showed how to run it in shadow mode.

Class 17 makes the gate operational: before spending tokens, the pipeline explains why a model is selected and what cost/latency tradeoff the team is accepting.

## Demo contrast

Use a documentation-only PR to show the fast route, then compare it with a refunds PR that selects the strong route.
