# Prompt - Tests adversariales OWASP

## Uso

Usa este prompt para pedir a la IA payloads adversariales contra una superficie concreta de `payments-svc`.

## Prompt

```md
Actua como red team de aplicaciones Python para `payments-svc`.

Quiero generar tests adversariales anclados en OWASP Top 10 para la superficie de busqueda de clientes.

Contexto:

- El repo tiene una funcion que busca clientes por email.
- Semgrep marco un riesgo de SQL injection por SQL construido con concatenacion.
- Tambien hay funciones seguras que usan parametros.

Objetivo:

Proponer payloads y casos de prueba para demostrar si la superficie es explotable.

Incluye familias:

- OWASP A03 Injection: payloads de SQL injection.
- Entradas malformadas: strings vacios, espacios y caracteres de control.
- Valores de frontera: strings largos.
- Comparacion contra una ruta segura o parametrizada si existe.

Reglas:

- No inventes endpoints si el repo solo expone funciones.
- Usa los nombres reales de funciones y archivos del repo.
- Cada payload debe tener objetivo, expectativa segura y razon del riesgo.
- No pidas dependencias externas.
- Devuelve una lista que pueda convertirse en `samples/security/adversarial-payloads.json` y `tests/test_adversarial.py`.
```
