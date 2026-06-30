# Router de revision - payments-svc

## Objetivo

Divide un diff de PR por tipo de archivo y decide que prompt especializado debe revisar cada bloque.

No hagas hallazgos de codigo en este paso.
No mezcles archivos de tipos distintos en el mismo bloque.
No cambies el contenido del diff.

## Rutas

- Python: archivos `.py`, usar `prompts/reviewer-python.md`.
- TypeScript: archivos `.ts` o `.tsx`, usar `prompts/reviewer-typescript.md`.
- Infraestructura: archivos `.yml` o `.yaml`, usar `prompts/reviewer-infra.md`.

## Salida obligatoria

Crea un archivo JSON dentro de `samples/reviews/`.
El nombre del archivo debe describir el ruteo del PR en kebab-case y terminar en `.json`.
Ejemplo de nombre: `routing-manual-refund.json`.

El contenido del archivo debe ser JSON valido con esta forma:

```json
{
  "routes": [
    {
      "name": "python",
      "prompt": "prompts/reviewer-python.md",
      "files": ["src/payments_svc/api.py"]
    },
    {
      "name": "typescript",
      "prompt": "prompts/reviewer-typescript.md",
      "files": ["web/src/refunds.ts"]
    },
    {
      "name": "infra",
      "prompt": "prompts/reviewer-infra.md",
      "files": [".github/workflows/review.yml"]
    }
  ]
}
```

Si un tipo de archivo no aparece en el diff, omite esa ruta.
