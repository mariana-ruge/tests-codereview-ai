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


def offline_verdict(diff: str, model: str) -> dict[str, Any]:
    changed_files = []
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            changed_files.append(line.removeprefix("+++ b/"))
    summary = "Offline fallback review for: " + ", ".join(changed_files[:5])
    if not changed_files:
        summary = "Offline fallback review found no changed files in the diff."
    return {
        "schema_version": "1.0",
        "review_mode": "pull_request",
        "model": model,
        "diff_summary": summary,
        "action": "pass",
        "findings": [],
    }


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
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Generate a deterministic local verdict without calling OpenRouter.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    diff = read_text(args.diff)
    prompt = read_text(args.prompt)
    schema = load_json(args.schema)
    model = os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL)

    if args.offline:
        verdict = offline_verdict(diff, f"offline/{model}")
    else:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise SystemExit("OPENROUTER_API_KEY is required unless --offline is used.")
        print(f"Calling OpenRouter model: {model}", file=sys.stderr)
        response = call_openrouter(build_payload(prompt, diff, schema, model), api_key)
        verdict = extract_verdict(response)

    verdict.setdefault("model", model)
    write_json(args.out, verdict)
    print(f"Wrote AI review verdict to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
