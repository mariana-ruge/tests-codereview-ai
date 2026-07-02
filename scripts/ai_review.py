"""Run the CI AI reviewer against a pull request diff."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openai/gpt-4o-mini"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"Could not read {path}: {exc}") from exc


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path} is not valid JSON: {exc}") from exc


def build_payload(prompt: str, diff: str, schema: dict[str, Any], model: str) -> dict[str, Any]:
    user_message = (
        "Review this pull request diff and return only JSON matching the schema.\n\n"
        "```diff\n"
        f"{diff}\n"
        "```"
    )
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "payments_svc_ai_review",
                "strict": True,
                "schema": schema,
            },
        },
    }


def call_openrouter(payload: dict[str, Any], api_key: str) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        OPENROUTER_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/jsrsolarte/payments-svc",
            "X-OpenRouter-Title": "payments-svc AI review",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"OpenRouter returned HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Could not reach OpenRouter: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"OpenRouter returned non-JSON response: {exc}") from exc


def extract_verdict(response: dict[str, Any]) -> dict[str, Any]:
    try:
        content = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise SystemExit("OpenRouter response did not include choices[0].message.content") from exc
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"AI reviewer returned invalid JSON: {exc}\nRaw content:\n{content}") from exc


def index_added_lines(diff: str) -> dict[tuple[str, str], int]:
    line_index: dict[tuple[str, str], int] = {}
    current_file: str | None = None
    new_line: int | None = None

    for raw_line in diff.splitlines():
        if raw_line.startswith("+++ b/"):
            current_file = raw_line.removeprefix("+++ b/")
            continue
        if raw_line.startswith("@@"):
            marker = raw_line.split(" ")[2]
            start = marker.removeprefix("+").split(",")[0]
            try:
                new_line = int(start)
            except ValueError:
                new_line = None
            continue
        if current_file is None or new_line is None:
            continue
        if raw_line.startswith("+") and not raw_line.startswith("+++"):
            line_index[(current_file, raw_line[1:].strip())] = new_line
            new_line += 1
        elif raw_line.startswith("-") and not raw_line.startswith("---"):
            continue
        else:
            new_line += 1

    return line_index


def normalize_finding_lines(verdict: dict[str, Any], diff: str) -> None:
    line_index = index_added_lines(diff)
    findings = verdict.get("findings", [])
    if not isinstance(findings, list):
        return

    for finding in findings:
        if not isinstance(finding, dict):
            continue
        file_name = finding.get("file")
        evidence = finding.get("evidence")
        if not isinstance(file_name, str) or not isinstance(evidence, str):
            continue
        matched_line = line_index.get((file_name, evidence.strip()))
        if matched_line is not None:
            finding["line"] = matched_line


def normalize_verdict_action(verdict: dict[str, Any]) -> None:
    findings = verdict.get("findings", [])
    if not isinstance(findings, list) or not findings:
        verdict["action"] = "pass"
        return

    actions = [
        finding.get("action")
        for finding in findings
        if isinstance(finding, dict)
    ]
    if "block" in actions:
        verdict["action"] = "block"
    elif "warn" in actions:
        verdict["action"] = "warn"
    else:
        verdict["action"] = "warn"


def write_json(path: Path, data: dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"Could not write {path}: {exc}") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the payments-svc AI reviewer.")
    parser.add_argument("--diff", required=True, type=Path, help="Path to the pull request diff.")
    parser.add_argument("--out", required=True, type=Path, help="Path to write the verdict JSON.")
    parser.add_argument("--prompt", default=Path("prompts/ci-review.md"), type=Path)
    parser.add_argument("--schema", default=Path("schemas/ai-review.schema.json"), type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    diff = read_text(args.diff)
    prompt = read_text(args.prompt)
    schema = load_json(args.schema)
    model = os.environ.get("OPENROUTER_MODEL", "").strip() or DEFAULT_MODEL

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY is required.")
    print(f"Calling OpenRouter model: {model}", file=sys.stderr)
    response = call_openrouter(build_payload(prompt, diff, schema, model), api_key)
    verdict = extract_verdict(response)

    verdict["model"] = model
    normalize_finding_lines(verdict, diff)
    normalize_verdict_action(verdict)
    write_json(args.out, verdict)
    print(f"Wrote AI review verdict to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
