# Log de Respuestas DeepSeek
## Sesión: 20250811_103426
## Fecha: 2025-08-11 10:34:26
## Modo: PRODUCCIÓN

---

## Movimiento #1
**Fecha**: 2025-07-30  
**Descripción**: `SPEI ENVIADO BANAMEX      / 0076312440  002 2207250costco bnmx julio 28`  
**Monto**: $-2,036.49  
**Tiempo respuesta**: 12.07s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-30
- Descripción original: "SPEI ENVIADO BANAMEX      / 0076312440  002 2207250costco bnmx julio 28"
- Monto: $-2,036.49
- Referencia: 0076312440


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingre...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Pagos de Tarjetas",
  "cuenta_vinculada": "TDC BANAMEX COSTCO 783",
  "nota_ia": "El movimiento es un SPEI enviado a Banamex, relacionado con un pago a Costco, lo que sugiere un pago de tarjeta de crédito.",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI", "TDC + nombre banco", "Monto negativo en cuenta BBVA"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Pagos de Tarjetas",
  "cuenta_vinculada": "TDC BANAMEX COSTCO 783",
  "nota_ia": "El movimiento es un SPEI enviado a Banamex, relacionado con un pago a Costco, lo que sugiere un pago",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI",
    "TDC + nombre banco",
    "Monto negativo en cuenta BBVA"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Pagos de Tarjetas  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: TDC BANAMEX COSTCO 783

---

## Movimiento #2
**Fecha**: 2025-07-30  
**Descripción**: `SPEI RECIBIDOBANCOPPEL    / 0141401703  137 9990008Yaris`  
**Monto**: $3,200.00  
**Tiempo respuesta**: 9.77s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-30
- Descripción original: "SPEI RECIBIDOBANCOPPEL    / 0141401703  137 9990008Yaris"
- Monto: $3,200.00
- Referencia: 0141401703


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos ISP
- Ingres...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "INGRESO",
  "categoria": "Ingresos Renta Yaris",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un ingreso por renta del vehículo Yaris, identificado en la descripción.",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI RECIBIDO", "Monto positivo en cuenta BBVA", "Descripción incluye 'Yaris'"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "INGRESO",
  "categoria": "Ingresos Renta Yaris",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un ingreso por renta del vehículo Yaris, identificado en la descripción.",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI RECIBIDO",
    "Monto positivo en cuenta BBVA",
    "Descripción incluye 'Yaris'"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: INGRESO
- ✅ **Categoría**: Ingresos Renta Yaris  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: None

---

## Movimiento #3
**Fecha**: 2025-07-28  
**Descripción**: `PAGO TARJETA DE CREDITO   /  2734443810     CUENTA:                  BMOV`  
**Monto**: $-10,961.40  
**Tiempo respuesta**: 11.81s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-28
- Descripción original: "PAGO TARJETA DE CREDITO   /  2734443810     CUENTA:                  BMOV"
- Monto: $-10,961.40
- Referencia: 2734443810


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- In...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Pagos de Tarjetas",
  "cuenta_vinculada": "TDC BBVA PLATINO 3358",
  "nota_ia": "El movimiento corresponde al pago de una tarjeta de crédito BBVA, identificada por el número de referencia y la descripción.",
  "confianza": 0.95,
  "reglas_aplicadas": ["Si contiene 'TDC' + nombre banco → Es pago de tarjeta de crédito", "Si es monto negativo de cuenta BBVA → Generalmente gasto o transferencia saliente"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Pagos de Tarjetas",
  "cuenta_vinculada": "TDC BBVA PLATINO 3358",
  "nota_ia": "El movimiento corresponde al pago de una tarjeta de crédito BBVA, identificada por el número de refe",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "Si contiene 'TDC' + nombre banco → Es pago de tarjeta de crédito",
    "Si es monto negativo de cuenta BBVA → Generalmente gasto o transferencia saliente"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Pagos de Tarjetas  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: TDC BBVA PLATINO 3358

---

## Movimiento #4
**Fecha**: 2025-07-28  
**Descripción**: `SPEI RECIBIDOBANORTE      / 0130134951  072 0250728Sin informaci n`  
**Monto**: $6,350.00  
**Tiempo respuesta**: 9.49s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-28
- Descripción original: "SPEI RECIBIDOBANORTE      / 0130134951  072 0250728Sin informaci n"
- Monto: $6,350.00
- Referencia: 0130134951


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos IS...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": "TDB BANORTE 3172",
  "nota_ia": "Movimiento identificado como transferencia SPEI recibida desde Banorte, posiblemente entre cuentas propias.",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI", "nombres de bancos"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": "TDB BANORTE 3172",
  "nota_ia": "Movimiento identificado como transferencia SPEI recibida desde Banorte, posiblemente entre cuentas p",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI",
    "nombres de bancos"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Transferencia SPEI  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: TDB BANORTE 3172

---

## Movimiento #5
**Fecha**: 2025-07-28  
**Descripción**: `BANCO INVEX SA INST 13511 / DES051005PM6    pendiente`  
**Monto**: $-6,908.66  
**Tiempo respuesta**: 12.79s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-28
- Descripción original: "BANCO INVEX SA INST 13511 / DES051005PM6    pendiente"
- Monto: $-6,908.66
- Referencia: 


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos ISP
- Ingresos Renta Yar...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "GASTO",
  "categoria": "Pago Tarjeta Credito",
  "cuenta_vinculada": "TDC INVEX CERO 5616",
  "nota_ia": "El movimiento corresponde a un pago de tarjeta de crédito Invex, identificado por el nombre del banco y la referencia TDC.",
  "confianza": 0.95,
  "reglas_aplicadas": ["Si contiene TDC + nombre banco → Es pago de tarjeta de crédito", "Si es monto negativo de cuenta BBVA → Generalmente gasto o transferencia saliente"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "GASTO",
  "categoria": "Pago Tarjeta Credito",
  "cuenta_vinculada": "TDC INVEX CERO 5616",
  "nota_ia": "El movimiento corresponde a un pago de tarjeta de crédito Invex, identificado por el nombre del banc",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "Si contiene TDC + nombre banco → Es pago de tarjeta de crédito",
    "Si es monto negativo de cuenta BBVA → Generalmente gasto o transferencia saliente"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: GASTO
- ✅ **Categoría**: Pago Tarjeta Credito  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: TDC INVEX CERO 5616

---

## Movimiento #6
**Fecha**: 2025-07-28  
**Descripción**: `SPEI RECIBIDOSPIN BY OXXO / 0127619554  728 0389310k`  
**Monto**: $258.00  
**Tiempo respuesta**: 9.54s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-28
- Descripción original: "SPEI RECIBIDOSPIN BY OXXO / 0127619554  728 0389310k"
- Monto: $258.00
- Referencia: 0127619554


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos ISP
- Ingresos Ren...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": "TDB SPIN OXXO 2113",
  "nota_ia": "El movimiento corresponde a una transferencia SPEI recibida desde OXXO, vinculada a la tarjeta de débito SPIN OXXO.",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI", "TDB"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": "TDB SPIN OXXO 2113",
  "nota_ia": "El movimiento corresponde a una transferencia SPEI recibida desde OXXO, vinculada a la tarjeta de dé",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI",
    "TDB"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Transferencia SPEI  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: TDB SPIN OXXO 2113

---

## Movimiento #7
**Fecha**: 2025-07-28  
**Descripción**: `PAGO DE PRESTAMO          / 9810848652      TOTAL DE RECIBO`  
**Monto**: $-14,002.80  
**Tiempo respuesta**: 9.80s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-28
- Descripción original: "PAGO DE PRESTAMO          / 9810848652      TOTAL DE RECIBO"
- Monto: $-14,002.80
- Referencia: 9810848652


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos ISP
- I...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "GASTO",
  "categoria": "Pago de Préstamo",
  "cuenta_vinculada": "PRESTAMOS REFIN25",
  "nota_ia": "El movimiento corresponde al pago de un préstamo, identificado por la descripción 'PAGO DE PRESTAMO' y la referencia numérica.",
  "confianza": 0.95,
  "reglas_aplicadas": ["Monto negativo en cuenta BBVA", "Descripción contiene 'PAGO DE PRESTAMO'"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "GASTO",
  "categoria": "Pago de Préstamo",
  "cuenta_vinculada": "PRESTAMOS REFIN25",
  "nota_ia": "El movimiento corresponde al pago de un préstamo, identificado por la descripción 'PAGO DE PRESTAMO'",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "Monto negativo en cuenta BBVA",
    "Descripción contiene 'PAGO DE PRESTAMO'"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: GASTO
- ✅ **Categoría**: Pago de Préstamo  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: PRESTAMOS REFIN25

---

## Movimiento #8
**Fecha**: 2025-07-25  
**Descripción**: `SPEI ENVIADO STP          / 0052319722  646 2207250k`  
**Monto**: $-500.00  
**Tiempo respuesta**: 10.75s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-25
- Descripción original: "SPEI ENVIADO STP          / 0052319722  646 2207250k"
- Monto: $-500.00
- Referencia: 0052319722


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos ISP
- Ingresos Re...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a una transferencia SPEI enviada, pero no se especifica la cuenta destino en las cuentas conocidas.",
  "confianza": 0.9,
  "reglas_aplicadas": ["SPEI", "monto negativo"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a una transferencia SPEI enviada, pero no se especifica la cuenta destino ",
  "confianza": 0.9,
  "reglas_aplicadas": [
    "SPEI",
    "monto negativo"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Transferencia SPEI  
- ✅ **Confianza**: 0.9
- ✅ **Cuenta vinculada**: None

---

## Movimiento #9
**Fecha**: 2025-07-24  
**Descripción**: `TEF RECIBIDO BANK OF AMER / 3229935321  106 00000011043696473509`  
**Monto**: $374.72  
**Tiempo respuesta**: 10.25s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-24
- Descripción original: "TEF RECIBIDO BANK OF AMER / 3229935321  106 00000011043696473509"
- Monto: $374.72
- Referencia: 3229935321


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos ISP
- ...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia Recibida",
  "cuenta_vinculada": "TDB BBVA 5019",
  "nota_ia": "Transferencia recibida desde Bank of America, posiblemente entre cuentas propias o pago de servicios.",
  "confianza": 0.9,
  "reglas_aplicadas": ["Si contiene nombres de bancos → Es transferencia", "Si es monto positivo a cuenta BBVA → Generalmente ingreso o transferencia entrante"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia Recibida",
  "cuenta_vinculada": "TDB BBVA 5019",
  "nota_ia": "Transferencia recibida desde Bank of America, posiblemente entre cuentas propias o pago de servicios",
  "confianza": 0.9,
  "reglas_aplicadas": [
    "Si contiene nombres de bancos → Es transferencia",
    "Si es monto positivo a cuenta BBVA → Generalmente ingreso o transferencia entrante"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Transferencia Recibida  
- ✅ **Confianza**: 0.9
- ✅ **Cuenta vinculada**: TDB BBVA 5019

---

## Movimiento #10
**Fecha**: 2025-07-20  
**Descripción**: `SPEI RECIBIDOMercado Pago / 0190782902  722 1238574MERCADO*PAGO`  
**Monto**: $6,094.00  
**Tiempo respuesta**: 11.02s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-20
- Descripción original: "SPEI RECIBIDOMercado Pago / 0190782902  722 1238574MERCADO*PAGO"
- Monto: $6,094.00
- Referencia: 0190782902


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos ISP
-...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "INGRESO",
  "categoria": "Ingresos Plataforma",
  "cuenta_vinculada": "TDB MPAGO 6007",
  "nota_ia": "Movimiento corresponde a un ingreso recibido desde Mercado Pago, probablemente por ventas o servicios a través de la plataforma.",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI RECIBIDO", "Monto positivo a cuenta BBVA", "Descripción incluye nombre de plataforma (Mercado Pago)"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "INGRESO",
  "categoria": "Ingresos Plataforma",
  "cuenta_vinculada": "TDB MPAGO 6007",
  "nota_ia": "Movimiento corresponde a un ingreso recibido desde Mercado Pago, probablemente por ventas o servicio",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI RECIBIDO",
    "Monto positivo a cuenta BBVA",
    "Descripción incluye nombre de plataforma (Mercado Pago)"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: INGRESO
- ✅ **Categoría**: Ingresos Plataforma  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: TDB MPAGO 6007

---

## Movimiento #11
**Fecha**: 2025-07-20  
**Descripción**: `SPEI RECIBIDOAZTECA       / 0190050210  127 5501950pago del mes de julio cruz`  
**Monto**: $270.00  
**Tiempo respuesta**: 11.08s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-20
- Descripción original: "SPEI RECIBIDOAZTECA       / 0190050210  127 5501950pago del mes de julio cruz"
- Monto: $270.00
- Referencia: 0190050210


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- In...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "INGRESO",
  "categoria": "Rentas",
  "cuenta_vinculada": "RENTA DE AZOTEA SIQUIEM / SNFCO ASIS",
  "nota_ia": "El movimiento corresponde a un SPEI recibido relacionado con un pago de renta de azotea.",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI", "Monto positivo a cuenta BBVA"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "INGRESO",
  "categoria": "Rentas",
  "cuenta_vinculada": "RENTA DE AZOTEA SIQUIEM / SNFCO ASIS",
  "nota_ia": "El movimiento corresponde a un SPEI recibido relacionado con un pago de renta de azotea.",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI",
    "Monto positivo a cuenta BBVA"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: INGRESO
- ✅ **Categoría**: Rentas  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: RENTA DE AZOTEA SIQUIEM / SNFCO ASIS

---

