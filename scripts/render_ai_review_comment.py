"""Render a reviewer-friendly pull request comment for an AI review verdict."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"Could not read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"{label} must be a JSON object.")
    return data


def shadow_message(action: str) -> str:
    if action == "block":
        return (
            "El revisor encontro algo que bloquearia el PR en un gate aplicado. "
            "En esta clase el gate esta en modo sombra, asi que el PR no se bloquea todavia por juicio del modelo."
        )
    if action == "warn":
        return (
            "El revisor encontro puntos que merecen atencion humana. "
            "El modo sombra los registra para comparar esa senal contra el criterio del equipo."
        )
    return (
        "El revisor no encontro problemas accionables en este diff. "
        "Ese resultado tambien queda como evidencia de calibracion."
    )


def finding_lines(findings: list[Any]) -> list[str]:
    if not findings:
        return ["No se reportaron hallazgos."]

    lines: list[str] = []
    for finding in findings:
        if not isinstance(finding, dict):
            continue
        title = finding.get("title", "Hallazgo sin titulo")
        action = finding.get("action", "report")
        severity = finding.get("severity", "unknown")
        category = finding.get("category", "unknown")
        file_name = finding.get("file", "unknown file")
        line = finding.get("line", "?")
        evidence = finding.get("evidence", "")
        recommendation = finding.get("recommendation", "")

        lines.append(f"- **{title}**")
        lines.append(f"  - Decision solicitada: `{action}` | Severidad: `{severity}` | Categoria: `{category}`")
        lines.append(f"  - Ubicacion: `{file_name}:{line}`")
        if evidence:
            lines.append(f"  - Evidencia: `{evidence}`")
        if recommendation:
            lines.append(f"  - Siguiente paso sugerido: {recommendation}")
    return lines


def plan_lines(plan: dict[str, Any] | None) -> list[str]:
    if not plan:
        return []
    return [
        "### Plan operativo",
        "",
        f"- Ruta: `{plan.get('route', 'unknown')}`",
        f"- Modelo seleccionado: `{plan.get('selected_model', 'unknown')}`",
        f"- Fuente del modelo: `{plan.get('selected_model_source', 'unknown')}`",
        f"- Cache: `{plan.get('cache_policy', 'unknown')}` con key `{plan.get('cache_key', 'unknown')}`",
        f"- Costo estimado: `{plan.get('estimated_cost', 'unknown')}`",
        f"- Objetivo de latencia: `{plan.get('latency_target_seconds', 'unknown')}s`",
        f"- Razon: {plan.get('reason', 'No se recibio razon de ruteo.')}",
        "",
    ]


def render_comment(verdict: dict[str, Any], mode: str, plan: dict[str, Any] | None) -> str:
    action = str(verdict.get("action", "unknown"))
    model = str(verdict.get("model", "unknown"))
    summary = str(verdict.get("diff_summary", "No se recibio resumen del diff."))
    findings = verdict.get("findings", [])
    if not isinstance(findings, list):
        findings = []

    lines = [
        "## Revision con IA",
        "",
        f"**Modo de rollout:** `{mode}`",
        f"**Veredicto solicitado por el modelo:** `{action}`",
        f"**Modelo:** `{model}`",
        "",
        "### Resumen",
        "",
        summary,
        "",
        "### Que significa",
        "",
        shadow_message(action) if mode == "shadow" else "El gate esta corriendo en modo aplicado.",
        "",
        *plan_lines(plan),
        "Este comentario esta escrito primero para la persona que revisa. El JSON queda abajo solo como evidencia de auditoria.",
        "",
        "### Hallazgos",
        "",
        *finding_lines(findings),
        "",
        "<details>",
        "<summary>JSON crudo del veredicto</summary>",
        "",
        "```json",
        json.dumps(verdict, indent=2, ensure_ascii=False),
        "```",
        "",
        "</details>",
    ]
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render an AI review PR comment.")
    parser.add_argument("verdict", type=Path)
    parser.add_argument("--mode", choices=["enforced", "shadow"], default="enforced")
    parser.add_argument("--plan", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    verdict = load_json_object(args.verdict, "Verdict")
    plan = load_json_object(args.plan, "Plan") if args.plan else None
    print(render_comment(verdict, args.mode, plan), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
