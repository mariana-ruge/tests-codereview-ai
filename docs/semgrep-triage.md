# Triage de Semgrep

## Contexto

Clase 11 usa Semgrep como scanner determinista y la IA como capa de triage.

La herramienta encontro hallazgos de seguridad. La IA no decide desde cero si el repo es seguro; recibe la salida de Semgrep y debe inspeccionar los archivos y lineas citados antes de clasificar con evidencia.

## Comandos ejecutados

```sh
semgrep --version
mkdir -p samples/semgrep
semgrep --config auto --json src > samples/semgrep/semgrep-results.json
cat samples/semgrep/semgrep-results.json
```

Version probada:

```text
1.168.0
```

Resumen de la corrida con `--config auto`:

```text
Findings: 4
Rules run: 1198
Targets scanned: 10

Finding 1: src/payments_svc/db.py:23
Rule: python.sqlalchemy.security.sqlalchemy-execute-raw-query.sqlalchemy-execute-raw-query

Finding 2: src/payments_svc/db.py:52
Rule: python.sqlalchemy.security.sqlalchemy-execute-raw-query.sqlalchemy-execute-raw-query

Finding 3: src/payments_svc/ops.py:13
Rule: python.lang.security.audit.subprocess-shell-true.subprocess-shell-true

Finding 4: src/payments_svc/ops.py:21
Rule: python.lang.security.audit.subprocess-shell-true.subprocess-shell-true
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
- 47-49: whitelist para estados permitidos.
- 51-52: segunda query marcada por Semgrep.

Archivo: `src/payments_svc/ops.py`

```python
subprocess.run(
    "python -m payments_svc.jobs " + job_name,
    shell=True,
    check=True,
)

subprocess.run(
    command,
    shell=True,
    check=True,
)
```

Lineas relevantes:

- 7-9: whitelist de jobs internos permitidos.
- 11-14: `shell=True` con comando construido desde job validado.
- 18-22: `shell=True` con comando recibido como parametro libre.

## Triage

| archivo | lineas | regla | clasificacion | justificacion | siguiente paso |
| --- | --- | --- | --- | --- | --- |
| `src/payments_svc/db.py` | 18-23 | `python.sqlalchemy.security.sqlalchemy-execute-raw-query.sqlalchemy-execute-raw-query` | `real` | La entrada `email` llega como parametro de `find_customer_by_email` y se concatena dentro del SQL en lineas 18-22. La query resultante se ejecuta en linea 23. No hay parametrizacion ni escape visible en el codigo. | Cambiar a query parametrizada y agregar test adversarial con payload de SQL injection en Clase 12. |
| `src/payments_svc/db.py` | 47-52 | `python.sqlalchemy.security.sqlalchemy-execute-raw-query.sqlalchemy-execute-raw-query` | `false_positive` | Semgrep marca concatenacion SQL en linea 51, pero el valor `status` se valida contra una whitelist cerrada en lineas 47-49 antes de construir la query. No parece explotable como inyeccion en este contexto. | No bloquear por seguridad. Como mejora de estilo, podria parametrizarse igual para reducir ruido futuro. |
| `src/payments_svc/ops.py` | 7-14 | `python.lang.security.audit.subprocess-shell-true.subprocess-shell-true` | `human_required` | Hay `shell=True` en linea 13, pero `job_name` se valida contra una whitelist en lineas 7-9. Falta contexto operacional: quien llama esta funcion, con que permisos corre y si el entorno del shell puede alterar el riesgo. | Pedir revision humana de permisos y entorno antes de decidir si bloquear. |
| `src/payments_svc/ops.py` | 18-22 | `python.lang.security.audit.subprocess-shell-true.subprocess-shell-true` | `real` | `command` entra como parametro libre en linea 18 y se ejecuta con `shell=True` en lineas 19-22. No hay whitelist ni tokenizacion visible. | Reemplazar por lista de argumentos con `shell=False` o limitar comandos permitidos. |

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
2 Code Findings
src/payments_svc/db.py
payments-sqli-string-concat
Lineas 18-22
Lineas 51
```

## Decision

La regla `payments-sqli-string-concat` queda como barrera candidata para CI en modo consultivo.

Todavia no se configura como gate bloqueante porque tambien detecta un caso con whitelist que clasificamos como `false_positive`. En Modulo C se demuestra localmente; en Modulo D se decide como integrarla al pipeline y como reducir ruido antes de bloquear.
