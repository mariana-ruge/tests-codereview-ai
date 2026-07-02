# LLM support audit

## Hallazgo

`src/payments_svc/llm_support.py` construye un prompt concatenando instrucciones internas, cuenta actual y entrada de usuario en un unico bloque de texto.

La misma ruta entrega al cliente LLM una herramienta de historial de refunds que puede consultar cualquier `account_id` recibido como argumento.

## Evidencia

Comando:

```sh
python scripts/check_llm_support.py
```

Salida esperada:

```text
[RISK] direct-system-prompt-leak
[RISK] confused-deputy-cross-account
[RISK] indirect-injection-note
LLM support checks with exposed risks: 3/3
```

## Riesgos

- Prompt injection directa: una consulta de usuario puede pedir ignorar instrucciones y revelar el system prompt.
- Prompt injection indirecta: contenido no confiable puede cargar instrucciones maliciosas dentro del contexto.
- Diputado confundido: una entrada de bajo privilegio puede activar una herramienta con acceso a datos de otra cuenta.

## Decision

La ruta LLM queda documentada como superficie vulnerable y no debe moverse a produccion sin controles adicionales.

El cliente fake permite demostrar el riesgo sin depender de proveedores externos ni de comportamiento no determinista.

## Mitigaciones

- Separar instrucciones del sistema, datos de usuario y datos recuperados por herramientas.
- Limitar herramientas por cuenta y por rol antes de entregarlas al flujo LLM.
- Validar que `account_id` de cualquier consulta de herramienta coincida con la cuenta autenticada.
- Filtrar la salida para impedir fuga de instrucciones internas.
- Registrar payloads adversariales como pruebas de regresion.
- Convertir este chequeo local en un gate de CI en Modulo D.

## Relacion con OWASP LLM

La demo ilustra riesgos alineados con prompt injection, exposicion de informacion sensible y agencia excesiva en aplicaciones con LLM.

La correccion no consiste solo en "mejorar el prompt": tambien requiere diseno de permisos, aislamiento de contexto y validaciones fuera del modelo.
