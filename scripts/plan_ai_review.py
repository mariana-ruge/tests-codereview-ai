"""Plan AI review routing before calling the model."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path


DEFAULT_FAST_MODEL = "openai/gpt-4o-mini"
DEFAULT_STRONG_MODEL = "openai/gpt-5.4-mini"
SECURITY_PATHS = (
    "src/payments_svc/db.py",
    "src/payments_svc/auth.py",
    "src/payments_svc/llm_support.py",
    "semgrep-rules/",
)
MONEY_PATHS = (
    "src/payments_svc/amounts.py",
    "src/payments_svc/refunds.py",
    "src/payments_svc/api.py",
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SystemExit(f"Could not read {path}: {exc}") from exc


def changed_files(diff: str) -> list[str]:
    files: list[str] = []
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            files.append(line.removeprefix("+++ b/"))
    return files


def added_line_count(diff: str) -> int:
    return sum(
        1
        for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )


def choose_route(files: list[str], added_lines: int) -> tuple[str, str, int, str]:
    if files and all(file.endswith(".md") or file.startswith("docs/") for file in files):
        return (
            "docs-only",
            "El diff solo cambia documentacion, asi que usa el modelo rapido y una meta corta de latencia.",
            30,
            "low",
        )
    if any(file.startswith(SECURITY_PATHS) for file in files):
        return (
            "security-sensitive",
            "El diff toca codigo o reglas sensibles de seguridad, asi que se selecciona el modelo fuerte.",
            90,
            "medium",
        )
    if any(file.startswith(MONEY_PATHS) for file in files):
        return (
            "payments-critical",
            "El diff toca dinero o comportamiento de refunds, asi que se selecciona el modelo fuerte.",
            90,
            "medium",
        )
    if added_lines > 120:
        return (
            "large-diff",
            "El diff es grande y requiere mas contexto de revision, asi que usa el modelo fuerte.",
            120,
            "medium",
        )
    return (
        "fast",
        "El diff es pequeno y no toca rutas sensibles, asi que usa el modelo rapido.",
        45,
        "low",
    )


def configured_model(env_name: str, default: str) -> tuple[str, str]:
    value = os.environ.get(env_name, "").strip()
    if value:
        return value, env_name
    return default, f"default:{env_name}"


def selected_model(route: str) -> tuple[str, str]:
    fast_model, fast_source = configured_model("OPENROUTER_MODEL_FAST", DEFAULT_FAST_MODEL)
    strong_model, strong_source = configured_model("OPENROUTER_MODEL_STRONG", DEFAULT_STRONG_MODEL)
    if route in {"security-sensitive", "payments-critical", "large-diff"}:
        return strong_model, strong_source
    return fast_model, fast_source


def build_plan(diff: str) -> dict[str, object]:
    files = changed_files(diff)
    added_lines = added_line_count(diff)
    digest = hashlib.sha256(diff.encode("utf-8")).hexdigest()
    route, reason, latency_target_seconds, estimated_cost = choose_route(files, added_lines)
    model, model_source = selected_model(route)
    return {
        "schema_version": "1.0",
        "route": route,
        "selected_model": model,
        "selected_model_source": model_source,
        "cache_key": digest[:16],
        "cache_policy": "report-only",
        "cache_hit": False,
        "changed_files": files,
        "added_lines": added_lines,
        "estimated_cost": estimated_cost,
        "latency_target_seconds": latency_target_seconds,
        "reason": reason,
    }


def write_github_env(path: Path, plan: dict[str, object]) -> None:
    env_file = os.environ.get("GITHUB_ENV")
    if not env_file:
        return
    with Path(env_file).open("a", encoding="utf-8") as file:
        file.write(f"OPENROUTER_MODEL={plan['selected_model']}\n")
        file.write(f"AI_REVIEW_PLAN={path.as_posix()}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plan AI review route and model selection.")
    parser.add_argument("diff", type=Path, help="Path to the pull request diff.")
    parser.add_argument("--out", type=Path, default=Path("ai-review-plan.json"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan = build_plan(read_text(args.diff))
    args.out.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_github_env(args.out, plan)

    print(f"Review route: {plan['route']}")
    print(f"Selected model: {plan['selected_model']}")
    print(f"Selected model source: {plan['selected_model_source']}")
    print(f"Cache key: {plan['cache_key']}")
    print(f"Estimated cost: {plan['estimated_cost']}")
    print(f"Latency target: {plan['latency_target_seconds']}s")
    print(f"Reason: {plan['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
