"""Validate a payments-svc AI review verdict."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


TOP_LEVEL_ACTIONS = {"pass", "warn", "block"}
FINDING_ACTIONS = {"report", "warn", "block"}
SEVERITIES = {"low", "medium", "high"}
CATEGORIES = {"security", "correctness", "tests", "maintainability", "unknown"}


class ValidationError(Exception):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValidationError(f"Could not read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError("Verdict must be a JSON object.")
    return data


def require_string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"`{key}` must be a non-empty string.")
    return value


def validate_finding(finding: Any, index: int) -> None:
    if not isinstance(finding, dict):
        raise ValidationError(f"findings[{index}] must be an object.")

    require_string(finding, "id")
    require_string(finding, "title")
    severity = require_string(finding, "severity")
    category = require_string(finding, "category")
    require_string(finding, "file")
    require_string(finding, "evidence")
    require_string(finding, "recommendation")
    action = require_string(finding, "action")

    line = finding.get("line")
    if not isinstance(line, int) or line < 1:
        raise ValidationError(f"findings[{index}].line must be a positive integer.")
    if severity not in SEVERITIES:
        raise ValidationError(f"findings[{index}].severity has unsupported value `{severity}`.")
    if category not in CATEGORIES:
        raise ValidationError(f"findings[{index}].category has unsupported value `{category}`.")
    if action not in FINDING_ACTIONS:
        raise ValidationError(f"findings[{index}].action has unsupported value `{action}`.")


def validate_verdict(verdict: dict[str, Any]) -> None:
    schema_version = require_string(verdict, "schema_version")
    if schema_version != "1.0":
        raise ValidationError("schema_version must be `1.0`.")

    review_mode = require_string(verdict, "review_mode")
    if review_mode != "pull_request":
        raise ValidationError("review_mode must be `pull_request`.")

    require_string(verdict, "model")
    require_string(verdict, "diff_summary")

    action = require_string(verdict, "action")
    if action not in TOP_LEVEL_ACTIONS:
        raise ValidationError(f"action has unsupported value `{action}`.")

    findings = verdict.get("findings")
    if not isinstance(findings, list):
        raise ValidationError("findings must be an array.")
    for index, finding in enumerate(findings):
        validate_finding(finding, index)

    if action == "pass" and findings:
        raise ValidationError("action cannot be `pass` when findings are present.")
    if any(finding["action"] == "block" for finding in findings) and action != "block":
        raise ValidationError("top-level action must be `block` when any finding blocks.")
    if action == "block" and not any(finding["action"] == "block" for finding in findings):
        raise ValidationError("top-level action is `block` but no finding blocks.")


def print_summary(verdict: dict[str, Any]) -> None:
    findings = verdict["findings"]
    print(f"Verdict: {verdict['action']}")
    print(f"Model: {verdict['model']}")
    print(f"Summary: {verdict['diff_summary']}")
    print(f"Findings: {len(findings)}")
    for finding in findings:
        location = f"{finding['file']}:{finding['line']}"
        print(f"- [{finding['action']}] {finding['title']} ({location})")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate an AI review verdict.")
    parser.add_argument("verdict", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        verdict = load_json(args.verdict)
        validate_verdict(verdict)
    except ValidationError as exc:
        print(f"Invalid AI review verdict: {exc}")
        return 1

    print_summary(verdict)
    return 2 if verdict["action"] == "block" else 0


if __name__ == "__main__":
    raise SystemExit(main())
