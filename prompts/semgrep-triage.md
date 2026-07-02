# Prompt - Triage de hallazgos Semgrep

## Uso

Usa este prompt despues de correr Semgrep. La IA no escanea el repositorio desde cero: recibe la salida de Semgrep y debe inspeccionar en el repo los archivos y lineas citados por la herramienta.

## Prompt de triage

```md
Actua como revisor de seguridad para `payments-svc`.

Voy a darte:

1. La salida bruta de Semgrep.
2. Acceso al repositorio `payments-svc`.

Tu tarea es clasificar el hallazgo en una de estas categorias:

- `real`: el patron es explotable o representa un bug accionable en este contexto.
- `false_positive`: el patron fue marcado, pero aqui no es explotable o no aplica.
- `human_required`: falta contexto para decidir sin inventar.

Reglas:

- Usa solo la salida de Semgrep y los archivos del repo.
- Abre los archivos y lineas citados por Semgrep antes de clasificar.
- Cita lineas reales del archivo.
- No inventes contexto de infraestructura, base de datos, autenticacion o usuarios.
- Si necesitas una suposicion para decidir, clasifica como `human_required`.
- Propone un siguiente paso verificable.

Formato de salida:

| archivo | lineas | regla | clasificacion | justificacion | siguiente paso |
| --- | --- | --- | --- | --- | --- |
```

## Prompt para generar regla Semgrep

````md
Convierte este anti-patron confirmado en una regla Semgrep para Python:

Anti-patron:

- Una variable con nombre tipo `query`, `sql` o `statement` se construye concatenando strings con una variable de entrada.
- Luego esa query se ejecuta contra la base de datos.

Ejemplo vulnerable:

```python
query = (
    "SELECT id, email, status "
    "FROM customers "
    "WHERE email = '" + email + "'"
)
row = connection.execute(query).fetchone()
```

Requisitos:

- La regla debe vivir en `semgrep-rules/payments-sqli.yml`.
- Debe tener `id`, `message`, `severity`, `languages`, `metadata` y `patterns`.
- Debe detectar el ejemplo vulnerable.
- Debe recomendar queries parametrizadas.
- No incluyas Markdown en el YAML final.
````
