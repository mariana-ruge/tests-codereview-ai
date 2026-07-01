# Triage de Semgrep

## Contexto

Clase 11 usa Semgrep como scanner determinista y la IA como capa de triage.

La herramienta encontro un patron de SQL construido de forma insegura. La IA no decide desde cero si el repo es seguro; recibe el hallazgo, el codigo alrededor y debe clasificarlo con evidencia.

## Comandos ejecutados

```sh
semgrep --version
semgrep --config auto --json src
```

Version probada:

```text
1.168.0
```

Resumen de la corrida con `--config auto`:

```text
Findings: 1
Rules run: 290
Targets scanned: 8
Finding: src/payments_svc/db.py:23
Rule: python.sqlalchemy.security.sqlalchemy-execute-raw-query.sqlalchemy-execute-raw-query
Severity: ERROR
CWE: CWE-89 SQL Injection
OWASP: A03:2021 - Injection
```

## Codigo observado

Archivo: `src/payments_svc/db.py`

```python
query = (
    "SELECT id, email, status "
    "FROM customers "
    "WHERE email = '" + email + "'"
)
row = connection.execute(query).fetchone()
```

Lineas relevantes:

- 18-22: construccion de query con concatenacion.
- 23: ejecucion de la query construida.

## Triage

| archivo | lineas | regla | clasificacion | justificacion | siguiente paso |
| --- | --- | --- | --- | --- | --- |
| `src/payments_svc/db.py` | 18-23 | `python.sqlalchemy.security.sqlalchemy-execute-raw-query.sqlalchemy-execute-raw-query` | `real` | La entrada `email` llega como parametro de `find_customer_by_email` y se concatena dentro del SQL en lineas 18-22. La query resultante se ejecuta en linea 23. No hay parametrizacion ni escape visible en el codigo. | Cambiar a query parametrizada y agregar test adversarial con payload de SQL injection en Clase 12. |

## Regla generada con IA

Despues de confirmar el hallazgo como real, se pidio a la IA convertir el anti-patron en una regla Semgrep propia.

Artefacto:

```sh
semgrep-rules/payments-sqli.yml
```

La regla busca variables con nombre tipo `query`, `sql` o `statement` construidas mediante concatenacion de strings y valores variables.

## Validacion de la regla

Comando:

```sh
semgrep --config semgrep-rules/payments-sqli.yml src
```

Resultado:

```text
1 Code Finding
src/payments_svc/db.py
payments-sqli-string-concat
Lineas 18-22
```

## Decision

La regla `payments-sqli-string-concat` queda como barrera candidata para CI.

Todavia no se configura como gate bloqueante. En Modulo C se demuestra localmente; en Modulo D se decide como integrarla al pipeline.
