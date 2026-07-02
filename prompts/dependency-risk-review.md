# Prompt: analisis de dependencia sospechosa

Actua como revisor de seguridad de cadena de suministro para un servicio Python.

Contexto:

- El repositorio es `payments-svc`.
- La rama actual se trata como si fuera un Pull Request hacia `develop`.
- Revisa solo el manifiesto de dependencias y la salida del auditor que te comparto.
- No inventes informacion de GitHub, CI, reviewers, historial remoto ni reputacion de paquetes que no aparezca en la evidencia.

Entrada:

1. Contenido de `requirements.txt`.
2. Salida de:

```sh
python scripts/audit_dependencies.py requirements.txt
```

Tarea:

1. Identifica dependencias que parezcan alucinadas, inexistentes o sospechosas.
2. Explica por que el hallazgo puede convertirse en riesgo de slopsquatting.
3. Separa evidencia verificable de inferencias.
4. Propone mitigaciones concretas para este repositorio.
5. Redacta el resultado como un documento Markdown para `docs/slopsquatting-requests-ai-utils.md`.

Restricciones:

- No afirmes que un paquete es malicioso solo porque no existe.
- No recomiendes instalar la dependencia sospechosa.
- No propongas controles que requieran servicios externos no mencionados.
- Si falta evidencia, dilo explicitamente.

Formato de salida:

Devuelve solo Markdown, sin bloque de codigo envolvente, con estas secciones:

- `# Slopsquatting: requests-ai-utils`
- `## Hallazgo`
- `## Evidencia`
- `## Riesgo`
- `## Decision`
- `## Mitigaciones`
- `## Relacion con SBOM y NIST`
