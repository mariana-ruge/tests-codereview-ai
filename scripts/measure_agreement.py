from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
HUMAN_LABELS = ROOT / "samples" / "agreement" / "human-labels.json"
AI_LABELS = ROOT / "samples" / "agreement" / "ai-labels.json"
REPORT = ROOT / "docs" / "reporte-acuerdo.md"


@dataclass(frozen=True)
class Label:
    case_id: str
    category: str
    present: bool
    severity: str | None
    notes: str


@dataclass(frozen=True)
class Metrics:
    category: str
    cases: int
    agreement: float
    kappa: float
    tp: int
    tn: int
    fp: int
    fn: int
    policy: str


def load_labels(path: Path) -> dict[tuple[str, str], Label]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    labels: dict[tuple[str, str], Label] = {}

    for raw in payload["labels"]:
        label = Label(
            case_id=require_string(raw, "case_id"),
            category=require_string(raw, "category"),
            present=require_bool(raw, "present"),
            severity=raw.get("severity"),
            notes=require_string(raw, "notes"),
        )
        key = (label.case_id, label.category)
        if key in labels:
            raise ValueError(f"duplicated label: {label.case_id}/{label.category}")
        labels[key] = label

    return labels


def require_string(raw: dict[str, Any], field: str) -> str:
    value = raw.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def require_bool(raw: dict[str, Any], field: str) -> bool:
    value = raw.get(field)
    if not isinstance(value, bool):
        raise ValueError(f"{field} must be a boolean")
    return value


def cohen_kappa(human: list[bool], ai: list[bool]) -> float:
    total = len(human)
    observed = sum(1 for expected, actual in zip(human, ai) if expected == actual) / total

    human_yes = sum(human) / total
    human_no = 1 - human_yes
    ai_yes = sum(ai) / total
    ai_no = 1 - ai_yes
    expected = (human_yes * ai_yes) + (human_no * ai_no)

    if expected == 1:
        return 1.0 if observed == 1 else 0.0

    return (observed - expected) / (1 - expected)


def policy_for(metric: Metrics) -> str:
    if metric.kappa >= 0.8 and metric.agreement >= 0.8:
        return "block"
    if metric.kappa >= 0.4 and metric.agreement >= 0.7:
        return "warn"
    return "human_required"


def calculate_metrics(
    human_labels: dict[tuple[str, str], Label],
    ai_labels: dict[tuple[str, str], Label],
) -> list[Metrics]:
    if set(human_labels) != set(ai_labels):
        missing_ai = sorted(set(human_labels) - set(ai_labels))
        missing_human = sorted(set(ai_labels) - set(human_labels))
        raise ValueError(f"label sets differ. missing_ai={missing_ai}, missing_human={missing_human}")

    categories = sorted({category for _, category in human_labels})
    metrics: list[Metrics] = []

    for category in categories:
        keys = sorted(key for key in human_labels if key[1] == category)
        human = [human_labels[key].present for key in keys]
        ai = [ai_labels[key].present for key in keys]

        tp = sum(1 for expected, actual in zip(human, ai) if expected and actual)
        tn = sum(1 for expected, actual in zip(human, ai) if not expected and not actual)
        fp = sum(1 for expected, actual in zip(human, ai) if not expected and actual)
        fn = sum(1 for expected, actual in zip(human, ai) if expected and not actual)

        agreement = (tp + tn) / len(keys)
        kappa = cohen_kappa(human, ai)

        base = Metrics(
            category=category,
            cases=len(keys),
            agreement=agreement,
            kappa=kappa,
            tp=tp,
            tn=tn,
            fp=fp,
            fn=fn,
            policy="",
        )
        metrics.append(
            Metrics(
                category=base.category,
                cases=base.cases,
                agreement=base.agreement,
                kappa=base.kappa,
                tp=base.tp,
                tn=base.tn,
                fp=base.fp,
                fn=base.fn,
                policy=policy_for(base),
            )
        )

    return metrics


def render_report(metrics: list[Metrics]) -> str:
    lines = [
        "# Reporte de acuerdo IA-vs-humano",
        "",
        "Este reporte compara etiquetas humanas contra etiquetas normalizadas del revisor ruteado.",
        "La unidad de comparacion es binaria: para cada caso y categoria, el hallazgo esta presente o no.",
        "",
        "El dataset es pequeno y sirve para calibracion de demo, no como benchmark productivo.",
        "",
        "## Resumen por categoria",
        "",
        "| Categoria | Casos | Acuerdo | Kappa | TP | TN | FP | FN | Politica sugerida |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]

    for metric in metrics:
        lines.append(
            "| {category} | {cases} | {agreement:.0%} | {kappa:.2f} | {tp} | {tn} | {fp} | {fn} | `{policy}` |".format(
                category=metric.category,
                cases=metric.cases,
                agreement=metric.agreement,
                kappa=metric.kappa,
                tp=metric.tp,
                tn=metric.tn,
                fp=metric.fp,
                fn=metric.fn,
                policy=metric.policy,
            )
        )

    lines.extend(
        [
            "",
            "## Politica",
            "",
            "- `block`: puede bloquear cuando el hallazgo sea `blocker` y la categoria tenga acuerdo alto.",
            "- `warn`: comenta el hallazgo, pero no bloquea automaticamente.",
            "- `human_required`: requiere decision humana antes de bloquear.",
            "",
            "## Lectura",
            "",
            "El revisor no tiene la misma confiabilidad en todas las categorias.",
            "Las categorias con menor kappa deben usarse como senal de revision, no como gate automatico.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    human_labels = load_labels(HUMAN_LABELS)
    ai_labels = load_labels(AI_LABELS)
    metrics = calculate_metrics(human_labels, ai_labels)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(render_report(metrics), encoding="utf-8")
    print(f"wrote {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
