# Prompt: payloads para ruta LLM de soporte

Actua como revisor de seguridad de aplicaciones con LLM.

Contexto:

- El repositorio es `payments-svc`.
- La rama actual se trata como si fuera un Pull Request hacia `develop`.
- La ruta a revisar es `src/payments_svc/llm_support.py`.
- El sistema usa un cliente fake determinista; no debes asumir llamadas a proveedores externos.
- Revisa solo el codigo y evidencia que te comparto.
- No inventes informacion de GitHub, CI, reviewers, checks o historial remoto.

Tarea:

1. Propon payloads de prompt injection directa contra la ruta LLM.
2. Propon payloads indirectos que simulen instrucciones maliciosas incluidas en contenido de usuario.
3. Incluye un payload que intente revelar instrucciones internas.
4. Incluye un payload que intente usar la herramienta de historial de refunds para otra cuenta.
5. Explica que riesgo demuestra cada payload.
6. Redacta una seccion de mitigaciones para `docs/llm-support-audit.md`.

Restricciones:

- No pidas ejecutar llamadas reales a un proveedor LLM.
- No propongas exfiltrar secretos reales.
- No inventes datos de cuentas que no aparezcan en el codigo.
- Separa evidencia verificable de inferencias.

Formato esperado:

Devuelve Markdown con estas secciones:

- `## Payloads propuestos`
- `## Evidencia esperada`
- `## Riesgos`
- `## Mitigaciones`
