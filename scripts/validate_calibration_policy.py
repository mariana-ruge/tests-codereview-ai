"""Valida que la politica de calibracion tenga las secciones minimas."""

from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED_SECTIONS = (
    "## Proposito",
    "## Insumos usados",
    "## Trazabilidad operativa",
    "## Matriz de confianza",
    "## Acciones operativas",
    "## Impuesto de alucinacion",
    "## Zonas NO-IA",
    "## Protocolo de override",
    "## Promocion del gate",
    "## Politica de cambio",
)
EXPECTED_TERMS = (
    "VP",
    "FP",
    "FN",
    "VN",
    "Auto-aprobar",
    "Consultivo",
    "Requiere humano",
    "NO-IA",
    "Bloqueante",
    "security-sql-injection",
    "refund-over-refund",
    "tests-missing-critical-path",
    "docs-only-noise-control",
    "FAILURE-MODES.md",
    "tests/",
    "prompts/*.md",
    "semgrep-rules/",
    "review-history.json",
)


def table_rows_after(text: str, heading: str) -> list[str]:
    lines = text.splitlines()
    try:
        start = lines.index(heading)
    except ValueError:
        return []

    rows: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        if line.startswith("| `") or line.startswith("| Auto") or line.startswith("| Consultivo") or line.startswith("| Bloqueante") or line.startswith("| Requiere") or line.startswith("| NO-IA"):
            rows.append(line)
    return rows


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Valida CALIBRATION-POLICY.md.")
    parser.add_argument("policy", type=Path, help="Ruta a CALIBRATION-POLICY.md.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        text = args.policy.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"No se pudo leer {args.policy}: {exc}")
        return 1

    missing = [section for section in REQUIRED_SECTIONS if section not in text]
    missing_terms = [term for term in EXPECTED_TERMS if term not in text]
    if missing:
        print("Politica de calibracion invalida.")
        for section in missing:
            print(f"- Falta seccion: {section}")
        return 1
    if missing_terms:
        print("Politica de calibracion incompleta.")
        for term in missing_terms:
            print(f"- Falta decision o regla esperada: {term}")
        return 1

    print("Politica de calibracion valida.")
    print()
    print(f"Secciones validadas: {len(REQUIRED_SECTIONS)}")
    for section in REQUIRED_SECTIONS:
        print(f"- OK: {section.removeprefix('## ')}")

    print()
    print("Acciones de confianza detectadas:")
    for action in ("Auto-aprobar", "Consultivo", "Requiere humano", "NO-IA"):
        print(f"- {action}")

    print()
    print("Matriz de confusion detectada:")
    for term in ("VP", "FP", "FN", "VN"):
        print(f"- {term}")

    print()
    print("Decisiones del gate:")
    for row in table_rows_after(text, "## Promocion del gate"):
        cells = [cell.strip(" `") for cell in row.strip("|").split("|")]
        if len(cells) >= 3:
            print(f"- {cells[0]} -> {cells[1]}")

    print()
    print()
    print("Trazabilidad operativa: presente")
    print("- Catalogo de fallos")
    print("- Suite endurecida")
    print("- Prompts versionados")
    print("- Seguridad estatica")
    print("- Flywheel de datos")

    print()
    print("Zonas NO-IA: presentes")
    print("Protocolo de override: conectado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
