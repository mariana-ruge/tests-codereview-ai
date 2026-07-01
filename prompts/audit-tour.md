# Prompt - Tour antes de auditar

## Uso

Usa este prompt antes de pedir hallazgos sobre codigo legacy o codigo que la IA no conoce.

## Prompt del tour

```md
Antes de auditar este archivo, no critiques nada todavia.

Quiero que hagas un tour tecnico de `src/payments_svc/legacy/settlement.py` usando solo el codigo que te comparto.

Devuelve:

1. Responsabilidad principal del modulo.
2. Entradas que recibe y de donde vienen.
3. Salidas que produce y quien las consume.
4. Dependencias internas o externas que usa.
5. Flujo principal, paso a paso.
6. Supuestos que estas infiriendo y que deberia verificar manualmente.

Reglas:

- No inventes contexto fuera del archivo.
- No reportes bugs todavia.
- Si algo no se puede saber por el codigo, dilo explicitamente.
- Cita funciones o lineas cuando el codigo las haga visibles.

Al final agrega una seccion llamada `Punto de control` con una lista corta de cosas que yo debo confirmar antes de pedirte hallazgos.
```

## Prompt de hallazgos con evidencia

```md
Ahora que el tour fue verificado, audita `src/payments_svc/legacy/settlement.py`.

Busca bugs, riesgos de rendimiento y problemas de seguridad.

Reglas obligatorias:

- Cada hallazgo debe citar una linea o rango de lineas real del archivo.
- Si no puedes citar linea, no incluyas el hallazgo.
- No repitas problemas generales de arquitectura si no son accionables en este archivo.
- Prioriza hallazgos que puedan demostrarse con una prueba o una medicion.

Formato:

- `categoria`: correctness, security, performance, tests o maintainability.
- `severidad`: blocker, high, medium o low.
- `lineas`: linea o rango exacto.
- `evidencia`: que ves en el codigo.
- `riesgo`: que podria fallar en produccion.
- `siguiente paso`: prueba, medicion o cambio minimo recomendado.
```
