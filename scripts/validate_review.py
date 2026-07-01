from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ALLOWED_CATEGORIES = {
    "correctness",
    "security",
    "performance",
    "tests",
    "style",
    "documentation",
}

ALLOWED_SEVERITIES = {"blocker", "advisory", "info"}

REQUIRED_STRING_FIELDS = {
    "rule_id",
    "category",
    "severity",
    "message",
    "suggested_fix",
}


class ValidationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def validate_finding(finding: Any, index: int) -> None:
    prefix = f"finding[{index}]"

    require(isinstance(finding, dict), f"{prefix} must be an object")

    for field in REQUIRED_STRING_FIELDS:
        require(field in finding, f"{prefix}.{field} is required")
        require(isinstance(finding[field], str), f"{prefix}.{field} must be a string")
        require(bool(finding[field].strip()), f"{prefix}.{field} cannot be empty")

    require(
        finding["category"] in ALLOWED_CATEGORIES,
        f"{prefix}.category must be one of: {', '.join(sorted(ALLOWED_CATEGORIES))}",
    )
    require(
        finding["severity"] in ALLOWED_SEVERITIES,
        f"{prefix}.severity must be one of: {', '.join(sorted(ALLOWED_SEVERITIES))}",
    )

    require("location" in finding, f"{prefix}.location is required")
    location = finding["location"]
    require(isinstance(location, dict), f"{prefix}.location must be an object")

    require("file" in location, f"{prefix}.location.file is required")
    require(isinstance(location["file"], str), f"{prefix}.location.file must be a string")
    require(bool(location["file"].strip()), f"{prefix}.location.file cannot be empty")

    require("line" in location, f"{prefix}.location.line is required")
    require(isinstance(location["line"], int), f"{prefix}.location.line must be an integer")
    require(location["line"] >= 1, f"{prefix}.location.line must be >= 1")


def validate_review(payload: Any) -> None:
    require(isinstance(payload, list), "review output must be a JSON list")

    for index, finding in enumerate(payload):
        validate_finding(finding, index)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python scripts/validate_review.py <review-output.json>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_review(payload)
    except FileNotFoundError:
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}", file=sys.stderr)
        return 1
    except ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
