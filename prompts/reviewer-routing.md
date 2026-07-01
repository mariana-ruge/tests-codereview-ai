# Router de revision - payments-svc

## Objetivo

Divide un diff de cambios contra `develop` por tipo de archivo, aplica el criterio del prompt especializado correspondiente a cada bloque y consolida un unico review final.

Trata este diff como si fuera un Pull Request hacia `develop`, aunque no exista un PR real en GitHub.
Usa solo el diff mostrado y los archivos incluidos.
No inventes informacion de GitHub, CI o historial remoto.

No mezcles archivos de tipos distintos en el mismo bloque.
No cambies el contenido del diff.
No devuelvas un JSON de rutas.
Devuelve directamente el JSON final de hallazgos.

## Rutas internas

- Python: archivos `.py`, usar el criterio de `prompts/reviewer-python.md`.
- TypeScript: archivos `.ts` o `.tsx`, usar el criterio de `prompts/reviewer-typescript.md`.
- Infraestructura: archivos `.yml` o `.yaml`, usar el criterio de `prompts/reviewer-infra.md`.

## Proceso

1. Separa mentalmente el diff por tipo de archivo.
2. Evalua cada bloque con el foco del prompt especializado correspondiente.
3. Consolida hallazgos duplicados si varios bloques apuntan al mismo riesgo.
4. Devuelve una sola lista JSON con todos los hallazgos accionables.

## Salida obligatoria

Crea un archivo JSON dentro de `samples/reviews/`.
El nombre del archivo debe describir el review ruteado en kebab-case y terminar en `.json`.
Ejemplo de nombre: `manual-refund-routed-review.json`.

El contenido del archivo debe cumplir el mismo contrato de `prompts/reviewer.md`: una lista JSON de hallazgos.
Si no hay hallazgos, devuelve `[]`.

Cada hallazgo debe tener:

- `rule_id`
- `category`
- `severity`
- `location.file`
- `location.line`
- `message`
- `suggested_fix`

Valores permitidos para `category`:

- `correctness`
- `security`
- `performance`
- `tests`
- `style`
- `documentation`

Valores permitidos para `severity`:

- `blocker`
- `advisory`
- `info`

Ejemplo minimo:

```json
[
  {
    "rule_id": "SEC-AUTHZ-001",
    "category": "security",
    "severity": "blocker",
    "location": {
      "file": "src/payments_svc/api.py",
      "line": 127
    },
    "message": "The admin refund endpoint constructs an admin user from request data instead of requiring an authenticated caller.",
    "suggested_fix": "Require an authenticated user from the request context and verify that the caller can refund the target account."
  }
]
```
