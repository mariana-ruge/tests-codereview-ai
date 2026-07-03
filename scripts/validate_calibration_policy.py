"""Valida que la politica de calibracion tenga las secciones minimas."""

from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED_SECTIONS = (
    "## Proposito",
    "## Insumos usados",
    "## Matriz de confianza",
    "## Acciones operativas",
    "## Impuesto de alucinacion",
    "## Zonas NO-IA",
    "## Protocolo de override",
    "## Reglas promovidas",
    "## Politica de cambio",
)


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
    if missing:
        print("Politica de calibracion invalida.")
        for section in missing:
            print(f"- Falta seccion: {section}")
        return 1

    print("Politica de calibracion valida.")
    print(f"Secciones requeridas: {len(REQUIRED_SECTIONS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
