# Auditoria de settlement.py

## Tour verificado

`src/payments_svc/legacy/settlement.py` construye un reporte diario de liquidacion por comercio.

Responsabilidad principal:

- Recibir una fecha de liquidacion, un repositorio y un convertidor de FX.
- Cargar comercios pendientes de liquidacion.
- Calcular para cada comercio montos brutos, fees, refunds, ajustes, reserva y neto.
- Devolver un `SettlementReport` con lineas por comercio y totales agregados.

Entradas:

- `settlement_date`: fecha del ciclo de liquidacion.
- `repository`: implementa `SettlementRepository` y entrega comercios, batches y ajustes.
- `fx_rates`: implementa `FxRates` y convierte montos entre monedas.
- `target_currency`: moneda final del reporte, por defecto `USD`.

Salidas:

- `SettlementReport`, con `SettlementLine` por comercio y totales de gross, fees, refunds, ajustes, reserva y neto.

Dependencias:

- `SettlementRepository` para datos de liquidacion.
- `FxRates` para conversion de moneda.
- `Decimal` para calculos monetarios.

Flujo principal:

1. `build_settlement_report` obtiene comercios en linea 85.
2. Recorre cada comercio desde linea 88.
3. Carga el batch de pagos del comercio en linea 89.
4. Convierte gross, fees y refunds a la moneda objetivo entre lineas 90 y 107.
5. Calcula ajustes llamando `calculate_adjustment_total` entre lineas 108 y 114.
6. Calcula reserva entre lineas 115 y 119.
7. Construye la linea de liquidacion entre lineas 123 y 134.
8. Devuelve el reporte agregado entre lineas 136 y 145.

Punto de control:

- Confirmar que el repositorio representa llamadas a base de datos o servicio externo.
- Confirmar si el volumen normal de comercios por liquidacion es alto.
- Confirmar si los ajustes manuales siempre estan en USD o si falta modelar moneda por ajuste.

## Hallazgos

### 1. Consulta por comercio dentro del loop de liquidacion

- `categoria`: performance
- `severidad`: high
- `lineas`: 88-89 y 108-156
- `evidencia`: `build_settlement_report` recorre todos los comercios en linea 88. Dentro de ese loop carga el batch por comercio en linea 89 y tambien calcula ajustes por comercio entre lineas 108 y 114. Esa funcion termina llamando `repository.load_manual_adjustments(merchant_id, settlement_date)` en linea 156.
- `riesgo`: si `repository` habla con base de datos, el reporte hace al menos una consulta por comercio para batch y otra para ajustes. Con cientos o miles de comercios, la liquidacion puede degradarse a un patron N+1 y crecer linealmente en llamadas remotas.
- `siguiente paso`: medir numero de llamadas del repositorio con 1, 10 y 100 comercios. Luego considerar una API batch, por ejemplo `load_payment_batches(settlement_date)` y `load_manual_adjustments_for_merchants(merchant_ids, settlement_date)`.

### 2. Supuesto implicito de moneda en ajustes manuales

- `categoria`: correctness
- `severidad`: medium
- `lineas`: 156-164
- `evidencia`: `SettlementAdjustment` no guarda moneda y `calculate_adjustment_total` convierte cada ajuste usando `source="USD"` en linea 162.
- `riesgo`: si un ajuste manual se registra en otra moneda, el reporte lo tratara como USD y el neto del comercio quedara incorrecto.
- `siguiente paso`: agregar `currency` a `SettlementAdjustment` o documentar y validar que todos los ajustes manuales se registran en USD.

## Regla de aceptacion

Hallazgo sin linea real se descarta. El hallazgo principal de rendimiento queda aceptado porque cita el loop y la llamada concreta al repositorio.
