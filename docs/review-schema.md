# Review verdict schema

El revisor de PRs debe devolver una lista JSON.

Cada item de la lista representa un hallazgo accionable.

## Campos

| Campo | Tipo | Requerido | Descripcion |
| --- | --- | --- | --- |
| `rule_id` | string | Si | Identificador estable de la regla violada. |
| `category` | string | Si | Categoria de la rubrica. |
| `severity` | string | Si | Severidad operativa para CI. |
| `location.file` | string | Si | Archivo donde aparece el hallazgo. |
| `location.line` | integer | Si | Linea del hallazgo. |
| `message` | string | Si | Explicacion breve del problema. |
| `suggested_fix` | string | Si | Correccion sugerida. |

## Categorias permitidas

- `correctness`
- `security`
- `performance`
- `tests`
- `style`
- `documentation`

## Severidades permitidas

- `blocker`
- `advisory`
- `info`

## Ejemplo valido

```json
[
  {
    "rule_id": "SEC-AUTHZ-001",
    "category": "security",
    "severity": "blocker",
    "location": {
      "file": "src/payments_svc/api.py",
      "line": 96
    },
    "message": "Manual refunds can be created without checking authentication or authorization.",
    "suggested_fix": "Require an authenticated user and verify refund permissions before creating a refund."
  }
]
```
