# Salida ejemplo - reviewer.md v1

## Correccion

Hallazgo en `src/payments_svc/api.py`: el endpoint `create_manual_refund` recibe `already_refunded`, pero no lo pasa a `request_refund`. Esto puede aprobar un reembolso manual aunque el pago ya tenga reembolsos parciales previos.

Correccion sugerida: pasar `already_refunded=Decimal(payload.already_refunded)` al calcular la decision.

## Seguridad

Hallazgo en `src/payments_svc/api.py`: el endpoint manual usa `account_id`, pero no verifica autenticacion ni autorizacion antes de procesar el reembolso.

Correccion sugerida: exigir usuario autenticado y validar permisos con una regla de autorizacion antes de llamar a `request_refund`.

## Rendimiento

Sin hallazgos.

## Tests faltantes

Hallazgo: el PR agrega un endpoint publico, pero no incluye tests que cubran autorizacion ni el caso donde `already_refunded` reduce el monto disponible.

Correccion sugerida: agregar tests de API para reembolso manual autorizado/no autorizado y para reembolso que excede el remanente.

## Estilo

Hallazgo en `src/payments_svc/api.py`: `account_id` se recibe como parametro de ruta, pero no se usa. Esto hace menos clara la intencion del endpoint.

Correccion sugerida: usar `account_id` en la verificacion de autorizacion o eliminarlo de la ruta.

## Documentacion

Hallazgo: `README.md` no documenta el nuevo endpoint de reembolso manual.

Correccion sugerida: agregar el endpoint y su comportamiento esperado a la documentacion publica.
