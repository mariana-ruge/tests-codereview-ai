# FAILURE-MODES.md - catalogo de fallos en payments-svc

Este archivo registra los modos de falla que aparecen al usar IA para generar pruebas y revisar codigo en `payments-svc`.

## Categoria: Generacion de tests

- [n1] La IA genera una suite que se ve completa, pero acepta la implementacion actual como contrato. Ejemplo: trata `calculate_fee(Decimal("0.00"), "USD") == Decimal("0.00")` como comportamiento esperado, aunque el contrato de negocio todavia debe discutirse.
- [n1] La IA cubre muchos casos nominales y de error, pero no distingue entre "esto pasa hoy" y "esto debe pasar". Ese salto convierte bugs sembrados en especificacion accidental.
- [n1] La IA introduce dependencias y estilo de test no pedidos. Ejemplo: usa `pytest`, aunque el plan del modulo propone empezar con comandos simples de `unittest`.
- [n1] La IA prueba helpers internos y constantes, pero no siempre valida los contratos de negocio relevantes para pagos: fee minimo, fronteras exactas, montos maximos combinados con fee y reglas de redondeo desde la perspectiva del producto.
- [n1] La IA no deja una trazabilidad clara entre cada test y un modo de falla. Sin catalogo previo, no sabemos que casos faltan, cuales sobran ni que riesgo cubre cada prueba.

## Categoria: Revision de codigo

- [n1] Una revision ingenua puede quedarse en estilo o cobertura aparente y no retar decisiones de negocio como `amount == 0`, redondeo bancario o reembolsos por encima del monto original.
- [n1] La IA puede dar por seguro que una funcion valida autenticacion o autorizacion solo porque el flujo compila y tiene nombres plausibles.

## Categoria: Dominio de pagos

- [n1] `amount == 0` es una frontera critica: debe decidirse explicitamente si aplica fee minimo, devuelve cero o se rechaza.
- [n1] `refund_amount > original_amount` es una frontera critica: debe rechazarse, aunque la implementacion inicial lo aprueba como sentinel para futuras clases.
- [n1] El redondeo decimal debe probarse contra reglas de negocio, no solo contra el metodo de redondeo que hoy usa la implementacion.
