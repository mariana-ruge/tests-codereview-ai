# Slopsquatting: requests-ai-utils

## Hallazgo

`requirements.txt` contiene una dependencia sospechosa:

```txt
requests-ai-utils
```

La auditoria contra PyPI marca `requests-ai-utils` como `not_found`.

## Evidencia

Comando:

```sh
python scripts/audit_dependencies.py requirements.txt
```

Resultado esperado:

```text
| dependency | normalized | status | latest |
| --- | --- | --- | --- |
| `fastapi` | `fastapi` | `found` | ... |
| `uvicorn[standard]` | `uvicorn` | `found` | ... |
| `semgrep` | `semgrep` | `found` | ... |
| `requests-ai-utils` | `requests-ai-utils` | `not_found` | - |

Potential hallucinated dependencies:
- requests-ai-utils
```

## Riesgo

`requests-ai-utils` suena plausible porque combina un paquete conocido (`requests`) con una utilidad asociada a IA, pero no existe en PyPI al momento de la auditoria.

Si un atacante registra ese nombre y el equipo instala el manifiesto sin verificarlo, una sugerencia alucinada puede convertirse en un ataque de cadena de suministro.

Esto es slopsquatting: aprovechar nombres de paquetes plausibles que la IA puede inventar y que luego alguien instala por confianza.

## Decision

`requests-ai-utils` no debe instalarse ni mantenerse en el manifiesto.

La existencia de una dependencia la decide el registro real, no la IA.

## Mitigaciones

- Eliminar `requests-ai-utils` del manifiesto.
- Verificar cada dependencia nueva contra PyPI antes de aprobarla.
- Preferir dependencias con proposito claro, mantenedores identificables y uso real.
- Agregar una auditoria continua de dependencias al pipeline en Modulo D.
- Cuando haya lockfile productivo, fijar versiones y evaluar hashes para el flujo de instalacion reproducible.

## Relacion con SBOM y NIST

Un SBOM debe representar lo que el software realmente incluye. Si el equipo acepta paquetes inventados por IA sin verificarlos, el inventario queda contaminado y puede certificar una dependencia inexistente o maliciosa.

Esta clase conecta con practicas de desarrollo seguro y gobierno de IA: la IA puede ayudar a explicar el riesgo, pero la verificacion debe ser determinista y trazable.
