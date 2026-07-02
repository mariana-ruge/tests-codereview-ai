"""Measure shadow-mode AI review agreement against human decisions."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ACTION_LEVELS = {
    "pass": 0,
    "report": 0,
    "warn": 1,
    "block": 2,
}


class MetricsError(Exception):
    pass


def load_runs(path: Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise MetricsError(f"Could not read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise MetricsError(f"{path} is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise MetricsError("Metrics input must be a JSON object.")
    if data.get("schema_version") != "1.0":
        raise MetricsError("schema_version must be `1.0`.")
    runs = data.get("runs")
    if not isinstance(runs, list) or not runs:
        raise MetricsError("runs must be a non-empty array.")

    for index, run in enumerate(runs):
        validate_run(run, index)
    return runs


def require_string(run: dict[str, Any], key: str, index: int) -> str:
    value = run.get(key)
    if not isinstance(value, str) or not value.strip():
        raise MetricsError(f"runs[{index}].{key} must be a non-empty string.")
    return value


def validate_run(run: Any, index: int) -> None:
    if not isinstance(run, dict):
        raise MetricsError(f"runs[{index}] must be an object.")

    require_string(run, "id", index)
    require_string(run, "pr", index)
    require_string(run, "rule", index)
    require_string(run, "category", index)
    require_string(run, "lesson", index)
    ai_action = require_string(run, "ai_action", index)
    human_action = require_string(run, "human_action", index)

    if ai_action not in ACTION_LEVELS:
        raise MetricsError(f"runs[{index}].ai_action has unsupported value `{ai_action}`.")
    if human_action not in ACTION_LEVELS:
        raise MetricsError(f"runs[{index}].human_action has unsupported value `{human_action}`.")


def classify(run: dict[str, Any]) -> str:
    ai_level = ACTION_LEVELS[run["ai_action"]]
    human_level = ACTION_LEVELS[run["human_action"]]
    if ai_level == human_level:
        return "agreement"
    if ai_level > human_level:
        return "false_positive"
    return "false_negative"


def percent(part: int, total: int) -> str:
    return f"{(part / total) * 100:.1f}%"


def promotion_hint(total: int, agreement: int, false_positive: int, false_negative: int) -> str:
    agreement_rate = agreement / total
    false_positive_rate = false_positive / total
    false_negative_rate = false_negative / total

    if total >= 3 and agreement_rate >= 0.9 and false_positive_rate == 0 and false_negative_rate <= 0.1:
        return "candidate: block"
    if total >= 2 and agreement_rate >= 0.7 and false_positive_rate <= 0.25:
        return "candidate: warn"
    return "keep: shadow"


def print_metrics(runs: list[dict[str, Any]]) -> None:
    by_rule: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for run in runs:
        by_rule[run["rule"]].append(run)

    totals = {"agreement": 0, "false_positive": 0, "false_negative": 0}
    for run in runs:
        totals[classify(run)] += 1

    total = len(runs)
    print(f"Gate runs: {total}")
    print(f"Operational agreement: {totals['agreement']}/{total} ({percent(totals['agreement'], total)})")
    print(f"False positives: {totals['false_positive']}")
    print(f"False negatives: {totals['false_negative']}")
    print("Decision: keep the gate in shadow except rules with strong agreement.")
    print()
    print("By rule:")

    for rule in sorted(by_rule):
        rule_runs = by_rule[rule]
        rule_totals = {"agreement": 0, "false_positive": 0, "false_negative": 0}
        for run in rule_runs:
            rule_totals[classify(run)] += 1

        count = len(rule_runs)
        hint = promotion_hint(
            count,
            rule_totals["agreement"],
            rule_totals["false_positive"],
            rule_totals["false_negative"],
        )
        print(
            "- "
            f"{rule}: {rule_totals['agreement']}/{count} agreement "
            f"({percent(rule_totals['agreement'], count)}), "
            f"FP {rule_totals['false_positive']}, "
            f"FN {rule_totals['false_negative']} -> {hint}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Measure AI review gate agreement.")
    parser.add_argument("runs", type=Path, help="Path to gate-runs.json.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        runs = load_runs(args.runs)
    except MetricsError as exc:
        print(f"Invalid gate metrics input: {exc}")
        return 1

    print_metrics(runs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
