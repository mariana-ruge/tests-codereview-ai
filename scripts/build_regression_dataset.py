"""Summarize AI review history as regression evidence."""

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
OUTCOMES = {"agreement", "false_positive", "false_negative"}


class DatasetError(Exception):
    pass


def load_cases(path: Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise DatasetError(f"Could not read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise DatasetError(f"{path} is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise DatasetError("Input must be a JSON object.")
    if data.get("schema_version") != "1.0":
        raise DatasetError("schema_version must be `1.0`.")

    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise DatasetError("cases must be a non-empty array.")

    seen: set[str] = set()
    for index, case in enumerate(cases):
        validate_case(case, index, seen)
    return cases


def require_string(case: dict[str, Any], key: str, index: int) -> str:
    value = case.get(key)
    if not isinstance(value, str) or not value.strip():
        raise DatasetError(f"cases[{index}].{key} must be a non-empty string.")
    return value


def validate_case(case: Any, index: int, seen: set[str]) -> None:
    if not isinstance(case, dict):
        raise DatasetError(f"cases[{index}] must be an object.")

    case_id = require_string(case, "case_id", index)
    if case_id in seen:
        raise DatasetError(f"cases[{index}].case_id duplicates `{case_id}`.")
    seen.add(case_id)

    for key in (
        "source",
        "route",
        "model",
        "rule",
        "category",
        "lesson",
        "improvement",
    ):
        require_string(case, key, index)

    model_action = require_string(case, "model_action", index)
    human_action = require_string(case, "human_action", index)
    outcome = require_string(case, "outcome", index)

    if model_action not in ACTION_LEVELS:
        raise DatasetError(f"cases[{index}].model_action has unsupported value `{model_action}`.")
    if human_action not in ACTION_LEVELS:
        raise DatasetError(f"cases[{index}].human_action has unsupported value `{human_action}`.")
    if outcome not in OUTCOMES:
        raise DatasetError(f"cases[{index}].outcome has unsupported value `{outcome}`.")

    expected = classify(model_action, human_action)
    if outcome != expected:
        raise DatasetError(
            f"cases[{index}].outcome is `{outcome}`, expected `{expected}` "
            f"from model_action `{model_action}` and human_action `{human_action}`."
        )


def classify(model_action: str, human_action: str) -> str:
    model_level = ACTION_LEVELS[model_action]
    human_level = ACTION_LEVELS[human_action]
    if model_level == human_level:
        return "agreement"
    if model_level > human_level:
        return "false_positive"
    return "false_negative"


def percent(part: int, total: int) -> str:
    return f"{(part / total) * 100:.1f}%"


def recommendation(rule_cases: list[dict[str, Any]]) -> str:
    total = len(rule_cases)
    agreements = sum(1 for case in rule_cases if case["outcome"] == "agreement")
    false_positives = sum(1 for case in rule_cases if case["outcome"] == "false_positive")
    false_negatives = sum(1 for case in rule_cases if case["outcome"] == "false_negative")

    if total >= 2 and agreements == total and any(case["human_action"] == "block" for case in rule_cases):
        return "candidate: promote to block"
    if false_negatives:
        return "improve: strengthen prompt or route before promotion"
    if false_positives:
        return "improve: narrow policy and keep in shadow or warn"
    if agreements == total:
        return "stable: keep collecting evidence"
    return "keep: shadow"


def print_report(cases: list[dict[str, Any]]) -> None:
    totals = {"agreement": 0, "false_positive": 0, "false_negative": 0}
    by_rule: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for case in cases:
        totals[case["outcome"]] += 1
        by_rule[case["rule"]].append(case)

    total = len(cases)
    print(f"Regression cases: {total}")
    print(f"Agreement: {totals['agreement']}/{total} ({percent(totals['agreement'], total)})")
    print(f"False positives: {totals['false_positive']}")
    print(f"False negatives: {totals['false_negative']}")
    print()
    print("Recommended improvements:")

    for rule in sorted(by_rule):
        rule_cases = by_rule[rule]
        print(f"- {rule}: {recommendation(rule_cases)}")
        for case in rule_cases:
            print(f"  - {case['case_id']}: {case['improvement']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an AI review regression report.")
    parser.add_argument("history", type=Path, help="Path to review-history.json.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        cases = load_cases(args.history)
    except DatasetError as exc:
        print(f"Invalid review history: {exc}")
        return 1

    print_report(cases)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
