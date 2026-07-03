# Politica de calibracion del AI review

## Proposito

Esta politica define cuando `payments-svc` puede confiar en el revisor con IA, cuando debe usarlo como senal consultiva y cuando la decision queda obligatoriamente en manos humanas.

La politica no reemplaza el criterio del equipo. Lo vuelve explicito, medible y auditable.

## Insumos usados

- Historial de regresion: `samples/ci/review-history.json`.
- Protocolo de override: `docs/override-protocol.md`.
- Criterios de promocion: `docs/promotion-criteria.md`.
- Gate de CI: `.github/workflows/ai-review.yml`.

## Matriz de confianza

Esta matriz resume el cruce entre lo que dijo la IA y la decision humana. Los conteos vienen de los casos semilla del curso y del historial de regresion disponible al cierre.

| Categoria | VP | FP | FN | VN | Lectura |
| --- | ---: | ---: | ---: | ---: | --- |
| `security-sql-injection` | 1 | 0 | 0 | 0 | La IA detecto correctamente el riesgo cuando hubo evidencia directa. |
| `refund-over-refund` | 1 | 0 | 0 | 0 | La IA bloqueo correctamente una ruta que podia exceder el saldo reembolsable. |
| `tests-missing-critical-path` | 0 | 1 | 0 | 0 | La senal es util, pero el modelo fue mas estricto que el humano. |
| `docs-only-noise-control` | 0 | 0 | 0 | 1 | La IA paso correctamente un cambio documental sin impacto operativo. |
| `dependency-hallucination` | 0 | 0 | 0 | 0 | Riesgo conocido por auditorias previas; requiere humano hasta tener mas casos. |

Leyenda:

- VP: verdadero positivo, la IA marco un problema y el humano estuvo de acuerdo.
- FP: falso positivo, la IA marco un problema pero el humano no lo habria bloqueado.
- FN: falso negativo, la IA dejo pasar algo que el humano habria marcado.
- VN: verdadero negativo, la IA paso algo que el humano tambien pasaria.

## Decision por categoria

| Categoria | Evidencia actual | Costo de FP | Costo de FN | Accion de confianza |
| --- | --- | --- | --- | --- |
| `security-sql-injection` | VP alto para evidencia directa. | Medio: puede frenar PRs hasta parametrizar queries. | Alto: puede dejar una vulnerabilidad explotable. | Requiere humano si el contexto no esta completo; si la evidencia esta en el diff, puede promoverse a bloqueante. |
| `refund-over-refund` | VP alto en PR sensible de refunds. | Medio: puede exigir correccion o pruebas extra. | Alto: puede permitir perdida de dinero. | Requiere humano en cambios de negocio; puede promoverse a bloqueante cuando el riesgo de saldo esta en el diff. |
| `tests-missing-critical-path` | FP documentado. | Medio: ruido y friccion si bloquea demasiado. | Medio-alto si omite casos de dinero o seguridad. | Consultivo por defecto. |
| `docs-only-noise-control` | VN documentado. | Bajo. | Bajo. | Auto-aprobar si el diff no cambia comportamiento operativo. |
| `dependency-hallucination` | Riesgo conocido por slopsquatting y paquetes inventados. | Bajo-medio: revisar dependencias toma tiempo. | Alto: puede introducir dependencia insegura o inexistente. | Requiere humano antes de aceptar dependencias nuevas. |

## Acciones operativas

| Accion | Que significa | Cuando se usa |
| --- | --- | --- |
| Auto-aprobar | La IA puede pasar el caso sin comentario accionable. | Cambios triviales o documentales sin impacto operativo. |
| Consultivo | La IA comenta, pero no bloquea. | Senales utiles con falsos positivos tolerables. |
| Requiere humano | La IA puede asistir, pero no decide. | Cambios de alto riesgo o contexto incompleto. |
| NO-IA | La IA no debe actuar como decisor. | Zonas donde el costo de error exige revision humana obligatoria. |

## Impuesto de alucinacion

El impuesto de alucinacion mide cuanto esfuerzo extra necesita el equipo para verificar afirmaciones inventadas por la IA.

Para `payments-svc`, el impuesto se trata asi:

| Superficie | Riesgo | Politica |
| --- | --- | --- |
| Python y paquetes nuevos | Medio-alto por paquetes inexistentes o inseguros. | Toda dependencia nueva requiere revision humana. |
| SQL y acceso a datos | Alto por riesgo de inyeccion o lectura indebida. | Bloqueante con evidencia directa; humano obligatorio si el contexto no esta en el diff. |
| Reglas de CI o workflow | Medio por cambios que pueden esconder fallos. | Consultivo o humano segun impacto. |
| Texto de documentacion | Bajo si no cambia comportamiento operativo. | Auto-aprobar o modelo rapido. |

## Zonas NO-IA

La IA no decide en estas zonas:

- Criptografia, manejo de llaves o secretos.
- Core de autorizacion.
- Cambios regulatorios o legales.
- Cambios de pagos donde el contexto contable no esta en el diff.
- Decisiones de negocio sobre reembolsos excepcionales.

En estas zonas, la IA puede resumir riesgos o preparar preguntas, pero la aprobacion es humana.

## Protocolo de override

Todo override debe producir una entrada en `samples/ci/review-history.json`.

El flujo es:

1. La IA emite un veredicto.
2. Un humano decide si esta de acuerdo.
3. Si hay desacuerdo, el humano etiqueta el caso como `false_positive` o `false_negative`.
4. La IA puede ayudar a redactar la entrada del historial.
5. El humano valida `human_action`, `outcome`, `lesson` e `improvement`.
6. El pipeline valida el historial con `scripts/build_regression_dataset.py`.

## Promocion del gate

La accion de confianza dice como tratar la categoria. La promocion a bloqueante es un paso adicional del gate de CI: solo se aplica a reglas con evidencia suficiente, alto costo de falso negativo y una condicion verificable en el diff.

| Regla | Estado | Razon |
| --- | --- | --- |
| `security-sql-injection` | Bloqueante | Alto costo de falso negativo y evidencia directa en casos semilla. |
| `refund-over-refund` | Bloqueante en rutas de dinero | Alto costo de falso negativo para refunds y saldos. |
| `tests-missing-critical-path` | Consultivo | Senal util, pero con falso positivo de bloqueo documentado. |
| `docs-only-noise-control` | Auto-aprobar | Cambios documentales sin impacto operativo no deben gastar revision fuerte. |

## Politica de cambio

Antes de cambiar prompt, modelo, ruteo o reglas bloqueantes:

1. Ejecutar el historial de regresion.
2. Revisar falsos positivos y falsos negativos por categoria.
3. Actualizar esta politica si cambia la decision operacional.
4. Mantener el cambio en modo sombra si no hay evidencia suficiente.

## Cierre

La IA acelera el criterio, pero no lo reemplaza.

Esta politica existe para que el equipo sepa cuando confiar, cuando pedir ayuda humana y cuando no delegar la decision.
