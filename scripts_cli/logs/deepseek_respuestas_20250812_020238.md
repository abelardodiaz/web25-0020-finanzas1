# Log de Respuestas DeepSeek
## Sesión: 20250812_020238
## Fecha: 2025-08-12 02:02:38
## Modo: PRODUCCIÓN

---

## Movimiento #1
**Fecha**: 2025-07-30  
**Descripción**: `SPEI ENVIADO BANAMEX      / 0076312440  002 2207250costco bnmx julio 28`  
**Monto**: $-2,036.49  
**Tiempo respuesta**: 12.24s  

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
  "nota_ia": "El movimiento es un SPEI enviado a Banamex, relacionado con un pago a Costco, lo que sugiere un pago de tarjeta de crédito Banamex Costco.",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI", "TDC + nombre banco", "monto negativo en cuenta BBVA"]
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
    "monto negativo en cuenta BBVA"
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
**Tiempo respuesta**: 11.02s  

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
  "reglas_aplicadas": ["SPEI como transferencia entrante", "Descripción coincide con cuenta conocida"]
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
    "SPEI como transferencia entrante",
    "Descripción coincide con cuenta conocida"
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
**Tiempo respuesta**: 11.49s  

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
  "tipo": "GASTO",
  "categoria": "Pago Tarjeta Credito",
  "cuenta_vinculada": "TDC BBVA PLATINO 3358",
  "nota_ia": "El movimiento corresponde al pago de una tarjeta de crédito BBVA, identificada por el número de referencia y la descripción.",
  "confianza": 0.95,
  "reglas_aplicadas": ["Si contiene \"TDC\" + nombre banco → Es pago de tarjeta de crédito", "Si es monto negativo de cuenta BBVA → Generalmente gasto o transferencia saliente"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "GASTO",
  "categoria": "Pago Tarjeta Credito",
  "cuenta_vinculada": "TDC BBVA PLATINO 3358",
  "nota_ia": "El movimiento corresponde al pago de una tarjeta de crédito BBVA, identificada por el número de refe",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "Si contiene \"TDC\" + nombre banco → Es pago de tarjeta de crédito",
    "Si es monto negativo de cuenta BBVA → Generalmente gasto o transferencia saliente"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: GASTO
- ✅ **Categoría**: Pago Tarjeta Credito  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: TDC BBVA PLATINO 3358

---

## Movimiento #4
**Fecha**: 2025-07-28  
**Descripción**: `SPEI RECIBIDOBANORTE      / 0130134951  072 0250728Sin informaci n`  
**Monto**: $6,350.00  
**Tiempo respuesta**: 9.78s  

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
**Tiempo respuesta**: 11.90s  

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
  "categoria": "Pago Tarjeta Crédito",
  "cuenta_vinculada": "TDC INVEX CERO 5616",
  "nota_ia": "El movimiento corresponde a un pago de tarjeta de crédito de INVEX, detectado por el nombre del banco y el formato típico de pago de TDC.",
  "confianza": 0.95,
  "reglas_aplicadas": ["Si contiene 'TDC' + nombre banco → Es pago de tarjeta de crédito", "Si es monto negativo de cuenta BBVA → Generalmente gasto o transferencia saliente"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "GASTO",
  "categoria": "Pago Tarjeta Crédito",
  "cuenta_vinculada": "TDC INVEX CERO 5616",
  "nota_ia": "El movimiento corresponde a un pago de tarjeta de crédito de INVEX, detectado por el nombre del banc",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "Si contiene 'TDC' + nombre banco → Es pago de tarjeta de crédito",
    "Si es monto negativo de cuenta BBVA → Generalmente gasto o transferencia saliente"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: GASTO
- ✅ **Categoría**: Pago Tarjeta Crédito  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: TDC INVEX CERO 5616

---

## Movimiento #6
**Fecha**: 2025-07-28  
**Descripción**: `SPEI RECIBIDOSPIN BY OXXO / 0127619554  728 0389310k`  
**Monto**: $258.00  
**Tiempo respuesta**: 10.75s  

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
  "nota_ia": "Movimiento identificado como transferencia SPEI recibida desde OXXO, vinculada a la tarjeta de débito SPIN OXXO.",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI", "TDB SPIN OXXO 2113"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": "TDB SPIN OXXO 2113",
  "nota_ia": "Movimiento identificado como transferencia SPEI recibida desde OXXO, vinculada a la tarjeta de débit",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI",
    "TDB SPIN OXXO 2113"
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
**Tiempo respuesta**: 10.59s  

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
  "categoria": "Pago de Prestamo",
  "cuenta_vinculada": "PRESTAMOS REFIN25",
  "nota_ia": "El movimiento corresponde al pago de un préstamo, identificado por la descripción 'PAGO DE PRESTAMO' y la referencia numérica.",
  "confianza": 0.95,
  "reglas_aplicadas": ["monto negativo de cuenta BBVA", "descripción contiene 'PAGO DE PRESTAMO'"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "GASTO",
  "categoria": "Pago de Prestamo",
  "cuenta_vinculada": "PRESTAMOS REFIN25",
  "nota_ia": "El movimiento corresponde al pago de un préstamo, identificado por la descripción 'PAGO DE PRESTAMO'",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "monto negativo de cuenta BBVA",
    "descripción contiene 'PAGO DE PRESTAMO'"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: GASTO
- ✅ **Categoría**: Pago de Prestamo  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: PRESTAMOS REFIN25

---

## Movimiento #8
**Fecha**: 2025-07-25  
**Descripción**: `SPEI ENVIADO STP          / 0052319722  646 2207250k`  
**Monto**: $-500.00  
**Tiempo respuesta**: 9.86s  

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
  "nota_ia": "Movimiento identificado como transferencia SPEI enviada, pero no se detectó una cuenta destino específica en las cuentas conocidas.",
  "confianza": 0.9,
  "reglas_aplicadas": ["SPEI", "Monto negativo en cuenta BBVA"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": null,
  "nota_ia": "Movimiento identificado como transferencia SPEI enviada, pero no se detectó una cuenta destino espec",
  "confianza": 0.9,
  "reglas_aplicadas": [
    "SPEI",
    "Monto negativo en cuenta BBVA"
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
**Tiempo respuesta**: 11.76s  

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
  "categoria": "Transferencias Entre Cuentas",
  "cuenta_vinculada": "TDB BANORTE 3172",
  "nota_ia": "El movimiento indica una transferencia recibida desde Bank of America, posiblemente entre cuentas propias.",
  "confianza": 0.9,
  "reglas_aplicadas": ["Si contiene nombres de bancos → Es transferencia", "Si es monto positivo a cuenta BBVA → Generalmente ingreso o transferencia entrante"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencias Entre Cuentas",
  "cuenta_vinculada": "TDB BANORTE 3172",
  "nota_ia": "El movimiento indica una transferencia recibida desde Bank of America, posiblemente entre cuentas pr",
  "confianza": 0.9,
  "reglas_aplicadas": [
    "Si contiene nombres de bancos → Es transferencia",
    "Si es monto positivo a cuenta BBVA → Generalmente ingreso o transferencia entrante"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Transferencias Entre Cuentas  
- ✅ **Confianza**: 0.9
- ✅ **Cuenta vinculada**: TDB BANORTE 3172

---

## Movimiento #10
**Fecha**: 2025-07-20  
**Descripción**: `SPEI RECIBIDOMercado Pago / 0190782902  722 1238574MERCADO*PAGO`  
**Monto**: $6,094.00  
**Tiempo respuesta**: 11.70s  

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
  "reglas_aplicadas": ["SPEI RECIBIDO", "Monto positivo a cuenta BBVA"]
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
    "Monto positivo a cuenta BBVA"
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
**Tiempo respuesta**: 11.54s  

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
  "nota_ia": "El movimiento corresponde a un ingreso por renta de la azotea, identificado por la descripción 'pago del mes de julio cruz' y el monto positivo.",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI", "monto positivo a cuenta BBVA"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "INGRESO",
  "categoria": "Rentas",
  "cuenta_vinculada": "RENTA DE AZOTEA SIQUIEM / SNFCO ASIS",
  "nota_ia": "El movimiento corresponde a un ingreso por renta de la azotea, identificado por la descripción 'pago",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI",
    "monto positivo a cuenta BBVA"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: INGRESO
- ✅ **Categoría**: Rentas  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: RENTA DE AZOTEA SIQUIEM / SNFCO ASIS

---

## Movimiento #12
**Fecha**: 2025-07-21  
**Descripción**: `LIVERPOOL POR INTERNET    / ******0287      RFC: DLI 931201MI9 14:38 AUT: 765150`  
**Monto**: $-2,040.40  
**Tiempo respuesta**: 12.71s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-21
- Descripción original: "LIVERPOOL POR INTERNET    / ******0287      RFC: DLI 931201MI9 14:38 AUT: 765150"
- Monto: $-2,040.40
- Referencia: ******0287


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 14...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "GASTO",
  "categoria": "Compras en Tiendas",
  "cuenta_vinculada": "TDC LIVERPOOL I300005028 9045",
  "nota_ia": "El movimiento corresponde a una compra en Liverpool, detectada por la descripción y la referencia a la tarjeta de Liverpool en las cuentas conocidas.",
  "confianza": 0.95,
  "reglas_aplicadas": ["Monto negativo en cuenta BBVA", "Descripción contiene nombre de tienda", "Referencia a TDC en cuentas conocidas"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "GASTO",
  "categoria": "Compras en Tiendas",
  "cuenta_vinculada": "TDC LIVERPOOL I300005028 9045",
  "nota_ia": "El movimiento corresponde a una compra en Liverpool, detectada por la descripción y la referencia a ",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "Monto negativo en cuenta BBVA",
    "Descripción contiene nombre de tienda",
    "Referencia a TDC en cuentas conocidas"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: GASTO
- ✅ **Categoría**: Compras en Tiendas  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: TDC LIVERPOOL I300005028 9045

---

## Movimiento #13
**Fecha**: 2025-07-21  
**Descripción**: `D LOCAL*STARLINK          / ******0287      RFC: EME 200630JP1 01:08 AUT: 165554`  
**Monto**: $-1,100.00  
**Tiempo respuesta**: 10.63s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-21
- Descripción original: "D LOCAL*STARLINK          / ******0287      RFC: EME 200630JP1 01:08 AUT: 165554"
- Monto: $-1,100.00
- Referencia: ******0287


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 14...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "GASTO",
  "categoria": "Servicios Internet",
  "cuenta_vinculada": "STARLINK RINCON1",
  "nota_ia": "El movimiento corresponde a un pago por servicios de internet de Starlink, identificado por la descripción 'D LOCAL*STARLINK' y la cuenta conocida 'STARLINK RINCON1'.",
  "confianza": 0.95,
  "reglas_aplicadas": ["Monto negativo en cuenta BBVA", "Descripción coincide con servicio conocido"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "GASTO",
  "categoria": "Servicios Internet",
  "cuenta_vinculada": "STARLINK RINCON1",
  "nota_ia": "El movimiento corresponde a un pago por servicios de internet de Starlink, identificado por la descr",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "Monto negativo en cuenta BBVA",
    "Descripción coincide con servicio conocido"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: GASTO
- ✅ **Categoría**: Servicios Internet  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: STARLINK RINCON1

---

## Movimiento #14
**Fecha**: 2025-07-18  
**Descripción**: `SPEI ENVIADO STP          / 0074463111  646 1207250ad`  
**Monto**: $-500.00  
**Tiempo respuesta**: 9.76s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-18
- Descripción original: "SPEI ENVIADO STP          / 0074463111  646 1207250ad"
- Monto: $-500.00
- Referencia: 0074463111


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos ISP
- Ingresos R...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a una transferencia SPEI enviada, pero no se especifica la cuenta destino en las cuentas conocidas.",
  "confianza": 0.95,
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
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI",
    "monto negativo"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Transferencia SPEI  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: None

---

## Movimiento #15
**Fecha**: 2025-07-18  
**Descripción**: `STRIPE *SYSCOM MX         / ******0287      RFC: SSC 840823JT3 10:33 AUT: 467028`  
**Monto**: $-293.82  
**Tiempo respuesta**: 10.01s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-18
- Descripción original: "STRIPE *SYSCOM MX         / ******0287      RFC: SSC 840823JT3 10:33 AUT: 467028"
- Monto: $-293.82
- Referencia: ******0287


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "GASTO",
  "categoria": "Compras en línea",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un pago realizado a Stripe, probablemente por una compra en línea en SYSCOM MX.",
  "confianza": 0.95,
  "reglas_aplicadas": ["Monto negativo en cuenta BBVA", "Descripción contiene proveedor de servicios"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "GASTO",
  "categoria": "Compras en línea",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un pago realizado a Stripe, probablemente por una compra en línea en SYS",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "Monto negativo en cuenta BBVA",
    "Descripción contiene proveedor de servicios"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: GASTO
- ✅ **Categoría**: Compras en línea  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: None

---

## Movimiento #16
**Fecha**: 2025-07-18  
**Descripción**: `SPEI RECIBIDOBANORTE      / 0182558252  072 0250718Pedro Antonio Sanchez Sanchez`  
**Monto**: $399.00  
**Tiempo respuesta**: 9.86s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-18
- Descripción original: "SPEI RECIBIDOBANORTE      / 0182558252  072 0250718Pedro Antonio Sanchez Sanchez"
- Monto: $399.00
- Referencia: 0182558252


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
-...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "INGRESO",
  "categoria": "Servicios Profesionales",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un SPEI recibido de Banorte, probablemente un pago por servicios profesionales de Pedro Antonio Sanchez Sanchez.",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI", "Monto positivo"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "INGRESO",
  "categoria": "Servicios Profesionales",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un SPEI recibido de Banorte, probablemente un pago por servicios profesi",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI",
    "Monto positivo"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: INGRESO
- ✅ **Categoría**: Servicios Profesionales  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: None

---

## Movimiento #17
**Fecha**: 2025-07-18  
**Descripción**: `SPEI RECIBIDOSPIN BY OXXO / 0181442188  728 0919388k`  
**Monto**: $8,560.00  
**Tiempo respuesta**: 11.09s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-18
- Descripción original: "SPEI RECIBIDOSPIN BY OXXO / 0181442188  728 0919388k"
- Monto: $8,560.00
- Referencia: 0181442188


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos ISP
- Ingresos R...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "INGRESO",
  "categoria": "Ingresos Renta Yaris",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un SPEI recibido, lo que indica un ingreso desde una fuente externa. La descripción incluye 'OXXO', pero no se vincula directamente con una cuenta conocida de gastos o transferencias.",
  "confianza": 0.85,
  "reglas_aplicadas": ["SPEI → Transferencia", "Monto positivo → Ingreso"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "INGRESO",
  "categoria": "Ingresos Renta Yaris",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un SPEI recibido, lo que indica un ingreso desde una fuente externa. La ",
  "confianza": 0.85,
  "reglas_aplicadas": [
    "SPEI → Transferencia",
    "Monto positivo → Ingreso"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: INGRESO
- ✅ **Categoría**: Ingresos Renta Yaris  
- ✅ **Confianza**: 0.85
- ✅ **Cuenta vinculada**: None

---

## Movimiento #18
**Fecha**: 2025-07-17  
**Descripción**: `STRIPE *SYSCOM MX         / ******0287      RFC: SSC 840823JT3 18:22 AUT: 097287`  
**Monto**: $-628.60  
**Tiempo respuesta**: 9.64s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-17
- Descripción original: "STRIPE *SYSCOM MX         / ******0287      RFC: SSC 840823JT3 18:22 AUT: 097287"
- Monto: $-628.60
- Referencia: ******0287


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "GASTO",
  "categoria": "Compras en línea",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un pago realizado a Stripe, probablemente por una compra en línea en SYSCOM MX.",
  "confianza": 0.95,
  "reglas_aplicadas": ["Monto negativo en cuenta BBVA", "Descripción de compra en línea"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "GASTO",
  "categoria": "Compras en línea",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un pago realizado a Stripe, probablemente por una compra en línea en SYS",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "Monto negativo en cuenta BBVA",
    "Descripción de compra en línea"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: GASTO
- ✅ **Categoría**: Compras en línea  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: None

---

## Movimiento #19
**Fecha**: 2025-07-17  
**Descripción**: `PAGO CUENTA DE TERCERO    /  0072819561     BNET    0468469393 pago`  
**Monto**: $400.00  
**Tiempo respuesta**: 9.67s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-17
- Descripción original: "PAGO CUENTA DE TERCERO    /  0072819561     BNET    0468469393 pago"
- Monto: $400.00
- Referencia: 0072819561


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos ISP...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Pago a Terceros",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento indica un pago a una cuenta de terceros a través de BNET, sin coincidencia con cuentas propias conocidas.",
  "confianza": 0.85,
  "reglas_aplicadas": ["Descripción contiene 'PAGO CUENTA DE TERCERO'"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Pago a Terceros",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento indica un pago a una cuenta de terceros a través de BNET, sin coincidencia con cuentas",
  "confianza": 0.85,
  "reglas_aplicadas": [
    "Descripción contiene 'PAGO CUENTA DE TERCERO'"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Pago a Terceros  
- ✅ **Confianza**: 0.85
- ✅ **Cuenta vinculada**: None

---

## Movimiento #20
**Fecha**: 2025-07-16  
**Descripción**: `SISTEMAS Y SERVICIOS      / GUIA:2111649    REF:5390392              CIE:0669911`  
**Monto**: $-765.77  
**Tiempo respuesta**: 9.74s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-16
- Descripción original: "SISTEMAS Y SERVICIOS      / GUIA:2111649    REF:5390392              CIE:0669911"
- Monto: $-765.77
- Referencia: 


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "GASTO",
  "categoria": "Servicios Digitales",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un pago por servicios digitales o sistemas, posiblemente relacionado con mantenimiento o suscripciones.",
  "confianza": 0.85,
  "reglas_aplicadas": ["Monto negativo en cuenta BBVA", "Descripción incluye 'SISTEMAS Y SERVICIOS'"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "GASTO",
  "categoria": "Servicios Digitales",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un pago por servicios digitales o sistemas, posiblemente relacionado con",
  "confianza": 0.85,
  "reglas_aplicadas": [
    "Monto negativo en cuenta BBVA",
    "Descripción incluye 'SISTEMAS Y SERVICIOS'"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: GASTO
- ✅ **Categoría**: Servicios Digitales  
- ✅ **Confianza**: 0.85
- ✅ **Cuenta vinculada**: None

---

## Movimiento #21
**Fecha**: 2025-07-15  
**Descripción**: `SPEI RECIBIDOHSBC         / 0165258183  021 0123456Internet Lourdes alvarado`  
**Monto**: $270.00  
**Tiempo respuesta**: 9.72s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-15
- Descripción original: "SPEI RECIBIDOHSBC         / 0165258183  021 0123456Internet Lourdes alvarado"
- Monto: $270.00
- Referencia: 0165258183


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ing...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "INGRESO",
  "categoria": "Servicios Profesionales",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un SPEI recibido desde HSBC, asociado a un pago por servicios profesionales de Lourdes Alvarado.",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI", "Monto positivo a cuenta BBVA"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "INGRESO",
  "categoria": "Servicios Profesionales",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un SPEI recibido desde HSBC, asociado a un pago por servicios profesiona",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI",
    "Monto positivo a cuenta BBVA"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: INGRESO
- ✅ **Categoría**: Servicios Profesionales  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: None

---

## Movimiento #22
**Fecha**: 2025-07-15  
**Descripción**: `SPEI RECIBIDOHSBC         / 0165252000  021 0123456Internet marisol alvarado`  
**Monto**: $270.00  
**Tiempo respuesta**: 10.94s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-15
- Descripción original: "SPEI RECIBIDOHSBC         / 0165252000  021 0123456Internet marisol alvarado"
- Monto: $270.00
- Referencia: 0165252000


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ing...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "INGRESO",
  "categoria": "Servicios Profesionales",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento es un SPEI recibido desde HSBC, lo que indica un ingreso desde una fuente externa, posiblemente por servicios profesionales prestados por Marisol Alvarado.",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI", "Monto positivo a cuenta BBVA"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "INGRESO",
  "categoria": "Servicios Profesionales",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento es un SPEI recibido desde HSBC, lo que indica un ingreso desde una fuente externa, pos",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI",
    "Monto positivo a cuenta BBVA"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: INGRESO
- ✅ **Categoría**: Servicios Profesionales  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: None

---

## Movimiento #23
**Fecha**: 2025-07-15  
**Descripción**: `SPEI ENVIADO STP          / 0056793919  646 0906250comida`  
**Monto**: $-435.00  
**Tiempo respuesta**: 10.13s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-15
- Descripción original: "SPEI ENVIADO STP          / 0056793919  646 0906250comida"
- Monto: $-435.00
- Referencia: 0056793919


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
  "tipo": "GASTO",
  "categoria": "Compra comida en la calle",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento describe una compra de comida con el término 'comida' en la descripción.",
  "confianza": 0.95,
  "reglas_aplicadas": ["Si es monto negativo de cuenta BBVA → Generalmente gasto o transferencia saliente", "Descripción contiene término relacionado con gasto"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "GASTO",
  "categoria": "Compra comida en la calle",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento describe una compra de comida con el término 'comida' en la descripción.",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "Si es monto negativo de cuenta BBVA → Generalmente gasto o transferencia saliente",
    "Descripción contiene término relacionado con gasto"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: GASTO
- ✅ **Categoría**: Compra comida en la calle  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: None

---

## Movimiento #24
**Fecha**: 2025-07-15  
**Descripción**: `PAGO CUENTA DE TERCERO    /  0074280869     BNET    0194446569 paraTCBanoete`  
**Monto**: $5,833.32  
**Tiempo respuesta**: 12.10s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-15
- Descripción original: "PAGO CUENTA DE TERCERO    /  0074280869     BNET    0194446569 paraTCBanoete"
- Monto: $5,833.32
- Referencia: 0074280869


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- I...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Pagos de Tarjetas",
  "cuenta_vinculada": "TDB BANORTE 3172",
  "nota_ia": "El movimiento describe un pago a una cuenta de terceros con referencia a BNET y un número de cuenta que coincide con el formato de TDB BANORTE 3172.",
  "confianza": 0.9,
  "reglas_aplicadas": ["Si contiene TDB + nombre banco → Es transferencia", "Si es monto negativo de cuenta BBVA → Generalmente transferencia saliente"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Pagos de Tarjetas",
  "cuenta_vinculada": "TDB BANORTE 3172",
  "nota_ia": "El movimiento describe un pago a una cuenta de terceros con referencia a BNET y un número de cuenta ",
  "confianza": 0.9,
  "reglas_aplicadas": [
    "Si contiene TDB + nombre banco → Es transferencia",
    "Si es monto negativo de cuenta BBVA → Generalmente transferencia saliente"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Pagos de Tarjetas  
- ✅ **Confianza**: 0.9
- ✅ **Cuenta vinculada**: TDB BANORTE 3172

---

## Movimiento #25
**Fecha**: 2025-07-15  
**Descripción**: `PAGO CUENTA DE TERCERO    /  0026149481     BNET    2914335600 abel`  
**Monto**: $4,000.00  
**Tiempo respuesta**: 10.95s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-15
- Descripción original: "PAGO CUENTA DE TERCERO    /  0026149481     BNET    2914335600 abel"
- Monto: $4,000.00
- Referencia: 0026149481


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos I...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Pago a Terceros",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento indica un pago a una cuenta de terceros a través de BNET, sin coincidencia con cuentas propias conocidas.",
  "confianza": 0.85,
  "reglas_aplicadas": ["Descripción contiene 'PAGO CUENTA DE TERCERO'", "No coincide con cuentas propias conocidas"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Pago a Terceros",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento indica un pago a una cuenta de terceros a través de BNET, sin coincidencia con cuentas",
  "confianza": 0.85,
  "reglas_aplicadas": [
    "Descripción contiene 'PAGO CUENTA DE TERCERO'",
    "No coincide con cuentas propias conocidas"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Pago a Terceros  
- ✅ **Confianza**: 0.85
- ✅ **Cuenta vinculada**: None

---

## Movimiento #26
**Fecha**: 2025-07-15  
**Descripción**: `SPEI ENVIADO BANORTE      / 0054907843  072 0906250k`  
**Monto**: $-5,835.00  
**Tiempo respuesta**: 10.63s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-15
- Descripción original: "SPEI ENVIADO BANORTE      / 0054907843  072 0906250k"
- Monto: $-5,835.00
- Referencia: 0054907843


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos ISP
- Ingresos ...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": "TDB BANORTE 3172",
  "nota_ia": "El movimiento corresponde a una transferencia SPEI enviada a una cuenta Banorte, identificada por el número de referencia y la descripción.",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI", "nombres de bancos", "monto negativo de cuenta BBVA"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": "TDB BANORTE 3172",
  "nota_ia": "El movimiento corresponde a una transferencia SPEI enviada a una cuenta Banorte, identificada por el",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI",
    "nombres de bancos",
    "monto negativo de cuenta BBVA"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Transferencia SPEI  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: TDB BANORTE 3172

---

## Movimiento #27
**Fecha**: 2025-07-14  
**Descripción**: `SPEI ENVIADO BAJIO        / 0099064105  030 09062504`  
**Monto**: $-65.00  
**Tiempo respuesta**: 11.80s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-14
- Descripción original: "SPEI ENVIADO BAJIO        / 0099064105  030 09062504"
- Monto: $-65.00
- Referencia: 0099064105


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
  "categoria": "Transferencias Entre Cuentas",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento contiene 'SPEI ENVIADO', lo que indica una transferencia saliente a otra cuenta, pero no se especifica la cuenta destino en las cuentas conocidas.",
  "confianza": 0.95,
  "reglas_aplicadas": ["Si contiene 'SPEI' o 'TRANSF' → Es transferencia", "Si es monto negativo de cuenta BBVA → Generalmente gasto o transferencia saliente"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencias Entre Cuentas",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento contiene 'SPEI ENVIADO', lo que indica una transferencia saliente a otra cuenta, pero ",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "Si contiene 'SPEI' o 'TRANSF' → Es transferencia",
    "Si es monto negativo de cuenta BBVA → Generalmente gasto o transferencia saliente"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Transferencias Entre Cuentas  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: None

---

## Movimiento #28
**Fecha**: 2025-07-13  
**Descripción**: `SPEI RECIBIDOAZTECA       / 0149630874  127 5501950julio 2025 pinot 132`  
**Monto**: $270.00  
**Tiempo respuesta**: 10.62s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-13
- Descripción original: "SPEI RECIBIDOAZTECA       / 0149630874  127 5501950julio 2025 pinot 132"
- Monto: $270.00
- Referencia: 0149630874


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "INGRESO",
  "categoria": "Rentas",
  "cuenta_vinculada": "RENTA DE AZOTEA SIQUIEM / SNFCO ASIS",
  "nota_ia": "El movimiento corresponde a un SPEI recibido relacionado con la renta de azotea, según la descripción.",
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
  "nota_ia": "El movimiento corresponde a un SPEI recibido relacionado con la renta de azotea, según la descripció",
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

## Movimiento #29
**Fecha**: 2025-07-12  
**Descripción**: `SPEI RECIBIDOBANORTE      / 0147497664  072 0250712av higueras 249`  
**Monto**: $270.00  
**Tiempo respuesta**: 9.33s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-12
- Descripción original: "SPEI RECIBIDOBANORTE      / 0147497664  072 0250712av higueras 249"
- Monto: $270.00
- Referencia: 0147497664


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos ISP
...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": "TDB BANORTE 3172",
  "nota_ia": "Movimiento identificado como transferencia SPEI recibida desde Banorte, posiblemente a una cuenta TDB Banorte.",
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
  "nota_ia": "Movimiento identificado como transferencia SPEI recibida desde Banorte, posiblemente a una cuenta TD",
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

## Movimiento #30
**Fecha**: 2025-07-12  
**Descripción**: `SPEI RECIBIDOAZTECA       / 0145831657  127 5501950pago del mes de junio cruz`  
**Monto**: $270.00  
**Tiempo respuesta**: 10.50s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-12
- Descripción original: "SPEI RECIBIDOAZTECA       / 0145831657  127 5501950pago del mes de junio cruz"
- Monto: $270.00
- Referencia: 0145831657


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
  "nota_ia": "El movimiento corresponde a un SPEI recibido relacionado con el pago de renta de la azotea, según la descripción.",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI", "Monto positivo en cuenta BBVA"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "INGRESO",
  "categoria": "Rentas",
  "cuenta_vinculada": "RENTA DE AZOTEA SIQUIEM / SNFCO ASIS",
  "nota_ia": "El movimiento corresponde a un SPEI recibido relacionado con el pago de renta de la azotea, según la",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI",
    "Monto positivo en cuenta BBVA"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: INGRESO
- ✅ **Categoría**: Rentas  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: RENTA DE AZOTEA SIQUIEM / SNFCO ASIS

---

## Movimiento #31
**Fecha**: 2025-07-11  
**Descripción**: `SPEI ENVIADO BANAMEX      / 0086553911  002 0906250julio 2025`  
**Monto**: $-8,500.00  
**Tiempo respuesta**: 10.66s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-11
- Descripción original: "SPEI ENVIADO BANAMEX      / 0086553911  002 0906250julio 2025"
- Monto: $-8,500.00
- Referencia: 0086553911


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
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": "TDB BANAMEX",
  "nota_ia": "Movimiento de salida por transferencia SPEI a Banamex, posiblemente a una cuenta propia o pago de servicio.",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI en descripción", "Monto negativo en cuenta BBVA", "Nombre de banco en descripción"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": "TDB BANAMEX",
  "nota_ia": "Movimiento de salida por transferencia SPEI a Banamex, posiblemente a una cuenta propia o pago de se",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI en descripción",
    "Monto negativo en cuenta BBVA",
    "Nombre de banco en descripción"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Transferencia SPEI  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: TDB BANAMEX

---

## Movimiento #32
**Fecha**: 2025-07-11  
**Descripción**: `RETIRO SIN TARJETA QR     / ******4662`  
**Monto**: $-500.00  
**Tiempo respuesta**: 10.33s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-11
- Descripción original: "RETIRO SIN TARJETA QR     / ******4662"
- Monto: $-500.00
- Referencia: ******4662


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos ISP
- Ingresos Renta Yaris
- PR...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "GASTO",
  "categoria": "Efectivo",
  "cuenta_vinculada": "CTA DEBITO EFECTIVO",
  "nota_ia": "Retiro de efectivo sin tarjeta, probablemente para uso personal o pago en efectivo.",
  "confianza": 0.95,
  "reglas_aplicadas": ["Si es monto negativo de cuenta BBVA → Generalmente gasto o transferencia saliente"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "GASTO",
  "categoria": "Efectivo",
  "cuenta_vinculada": "CTA DEBITO EFECTIVO",
  "nota_ia": "Retiro de efectivo sin tarjeta, probablemente para uso personal o pago en efectivo.",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "Si es monto negativo de cuenta BBVA → Generalmente gasto o transferencia saliente"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: GASTO
- ✅ **Categoría**: Efectivo  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: CTA DEBITO EFECTIVO

---

## Movimiento #33
**Fecha**: 2025-07-10  
**Descripción**: `SPEI ENVIADO SANTANDER    / 0083751678  014 0906250c142`  
**Monto**: $-800.00  
**Tiempo respuesta**: 10.47s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-10
- Descripción original: "SPEI ENVIADO SANTANDER    / 0083751678  014 0906250c142"
- Monto: $-800.00
- Referencia: 0083751678


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos ISP
- Ingresos...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": "SANTANDER",
  "nota_ia": "Transferencia SPEI enviada a una cuenta de Santander, posiblemente entre cuentas propias o pago a terceros.",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI", "nombres de bancos", "monto negativo de cuenta BBVA"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": "SANTANDER",
  "nota_ia": "Transferencia SPEI enviada a una cuenta de Santander, posiblemente entre cuentas propias o pago a te",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI",
    "nombres de bancos",
    "monto negativo de cuenta BBVA"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Transferencia SPEI  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: SANTANDER

---

## Movimiento #34
**Fecha**: 2025-07-10  
**Descripción**: `PAGO CUENTA DE TERCERO    /  0017653263     BNET    1506914864 jul 2025`  
**Monto**: $-500.00  
**Tiempo respuesta**: 10.12s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-10
- Descripción original: "PAGO CUENTA DE TERCERO    /  0017653263     BNET    1506914864 jul 2025"
- Monto: $-500.00
- Referencia: 0017653263


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingreso...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Pago a Terceros",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un pago a una cuenta de terceros a través de BNET.",
  "confianza": 0.90,
  "reglas_aplicadas": ["Si es monto negativo de cuenta BBVA → Generalmente gasto o transferencia saliente"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Pago a Terceros",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un pago a una cuenta de terceros a través de BNET.",
  "confianza": 0.9,
  "reglas_aplicadas": [
    "Si es monto negativo de cuenta BBVA → Generalmente gasto o transferencia saliente"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Pago a Terceros  
- ✅ **Confianza**: 0.9
- ✅ **Cuenta vinculada**: None

---

## Movimiento #35
**Fecha**: 2025-07-10  
**Descripción**: `SPEI RECIBIDOAZTECA       / 0133716599  127 5501950pago internet`  
**Monto**: $270.00  
**Tiempo respuesta**: 10.51s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-10
- Descripción original: "SPEI RECIBIDOAZTECA       / 0133716599  127 5501950pago internet"
- Monto: $270.00
- Referencia: 0133716599


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
  "tipo": "INGRESO",
  "categoria": "Servicios Profesionales",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un SPEI recibido, lo que indica un ingreso desde una fuente externa, posiblemente por servicios profesionales o pago de renta.",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI", "Monto positivo a cuenta BBVA"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "INGRESO",
  "categoria": "Servicios Profesionales",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un SPEI recibido, lo que indica un ingreso desde una fuente externa, pos",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI",
    "Monto positivo a cuenta BBVA"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: INGRESO
- ✅ **Categoría**: Servicios Profesionales  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: None

---

## Movimiento #36
**Fecha**: 2025-07-10  
**Descripción**: `SPEI RECIBIDOSANTANDER    / 0132945181  014 3985282TRANSFERENCIA`  
**Monto**: $270.00  
**Tiempo respuesta**: 8.67s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-10
- Descripción original: "SPEI RECIBIDOSANTANDER    / 0132945181  014 3985282TRANSFERENCIA"
- Monto: $270.00
- Referencia: 0132945181


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
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": null,
  "nota_ia": "Movimiento identificado como transferencia SPEI recibida desde otro banco (Santander).",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI", "TRANSFERENCIA"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": null,
  "nota_ia": "Movimiento identificado como transferencia SPEI recibida desde otro banco (Santander).",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI",
    "TRANSFERENCIA"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Transferencia SPEI  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: None

---

## Movimiento #37
**Fecha**: 2025-07-10  
**Descripción**: `SPEI RECIBIDOBANCOPPEL    / 0132927829  137 5041039Av higueras 215`  
**Monto**: $270.00  
**Tiempo respuesta**: 9.75s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-10
- Descripción original: "SPEI RECIBIDOBANCOPPEL    / 0132927829  137 5041039Av higueras 215"
- Monto: $270.00
- Referencia: 0132927829


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos ISP
...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": null,
  "nota_ia": "Movimiento identificado como transferencia SPEI recibida desde Bancoppel, pero no se especifica cuenta destino en BBVA.",
  "confianza": 0.90,
  "reglas_aplicadas": ["SPEI", "Transferencia entrante"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": null,
  "nota_ia": "Movimiento identificado como transferencia SPEI recibida desde Bancoppel, pero no se especifica cuen",
  "confianza": 0.9,
  "reglas_aplicadas": [
    "SPEI",
    "Transferencia entrante"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Transferencia SPEI  
- ✅ **Confianza**: 0.9
- ✅ **Cuenta vinculada**: None

---

## Movimiento #38
**Fecha**: 2025-07-09  
**Descripción**: `PAGO CUENTA DE TERCERO    /  0035016043     BNET    0194446569 traspaso`  
**Monto**: $19,639.54  
**Tiempo respuesta**: 9.93s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-09
- Descripción original: "PAGO CUENTA DE TERCERO    /  0035016043     BNET    0194446569 traspaso"
- Monto: $19,639.54
- Referencia: 0035016043


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
  "categoria": "Transferencias Entre Cuentas",
  "cuenta_vinculada": "BNET",
  "nota_ia": "El movimiento describe un traspaso a una cuenta de tercero, identificada como BNET.",
  "confianza": 0.9,
  "reglas_aplicadas": ["TRANSF", "nombres bancarios"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencias Entre Cuentas",
  "cuenta_vinculada": "BNET",
  "nota_ia": "El movimiento describe un traspaso a una cuenta de tercero, identificada como BNET.",
  "confianza": 0.9,
  "reglas_aplicadas": [
    "TRANSF",
    "nombres bancarios"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Transferencias Entre Cuentas  
- ✅ **Confianza**: 0.9
- ✅ **Cuenta vinculada**: BNET

---

## Movimiento #39
**Fecha**: 2025-07-09  
**Descripción**: `IVA COM SERV BCA INTERNET / IVA COM SERV BC`  
**Monto**: $-0.80  
**Tiempo respuesta**: 9.94s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-09
- Descripción original: "IVA COM SERV BCA INTERNET / IVA COM SERV BC"
- Monto: $-0.80
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
- Ingresos Renta Yaris
- PRESTAMOS...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "GASTO",
  "categoria": "Comisiones Bancarias",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un cobro de IVA por servicios bancarios de internet, clasificado como gasto por ser una salida de dinero por servicios.",
  "confianza": 0.95,
  "reglas_aplicadas": ["Si es monto negativo de cuenta BBVA → Generalmente gasto o transferencia saliente"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "GASTO",
  "categoria": "Comisiones Bancarias",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un cobro de IVA por servicios bancarios de internet, clasificado como ga",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "Si es monto negativo de cuenta BBVA → Generalmente gasto o transferencia saliente"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: GASTO
- ✅ **Categoría**: Comisiones Bancarias  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: None

---

## Movimiento #40
**Fecha**: 2025-07-09  
**Descripción**: `SERV BANCA INTERNET       / OPS SERV BCA IN`  
**Monto**: $-5.00  
**Tiempo respuesta**: 10.57s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-09
- Descripción original: "SERV BANCA INTERNET       / OPS SERV BCA IN"
- Monto: $-5.00
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
- Ingresos Renta Yaris
- PRESTAMOS...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "GASTO",
  "categoria": "Comisiones Bancarias",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un cobro por servicios de banca en línea, común en cuentas bancarias.",
  "confianza": 0.95,
  "reglas_aplicadas": ["Si es monto negativo de cuenta BBVA → Generalmente gasto o transferencia saliente", "Descripción relacionada con servicios bancarios"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "GASTO",
  "categoria": "Comisiones Bancarias",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un cobro por servicios de banca en línea, común en cuentas bancarias.",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "Si es monto negativo de cuenta BBVA → Generalmente gasto o transferencia saliente",
    "Descripción relacionada con servicios bancarios"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: GASTO
- ✅ **Categoría**: Comisiones Bancarias  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: None

---

## Movimiento #41
**Fecha**: 2025-07-08  
**Descripción**: `SPEI ENVIADO BANORTE      / 0074757497  072 0906250k`  
**Monto**: $-41,680.00  
**Tiempo respuesta**: 11.44s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-08
- Descripción original: "SPEI ENVIADO BANORTE      / 0074757497  072 0906250k"
- Monto: $-41,680.00
- Referencia: 0074757497


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos ISP
- Ingresos...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencias Entre Cuentas",
  "cuenta_vinculada": "TDB BANORTE 3172",
  "nota_ia": "Movimiento SPEI enviado a Banorte, probable transferencia entre cuentas propias.",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI en descripción", "Monto negativo en cuenta BBVA", "Nombre de banco en descripción"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencias Entre Cuentas",
  "cuenta_vinculada": "TDB BANORTE 3172",
  "nota_ia": "Movimiento SPEI enviado a Banorte, probable transferencia entre cuentas propias.",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI en descripción",
    "Monto negativo en cuenta BBVA",
    "Nombre de banco en descripción"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Transferencias Entre Cuentas  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: TDB BANORTE 3172

---

## Movimiento #42
**Fecha**: 2025-07-08  
**Descripción**: `SPEI RECIBIDOCONSUBANCO   / 0126852430  140 1847433K`  
**Monto**: $366.00  
**Tiempo respuesta**: 9.75s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-08
- Descripción original: "SPEI RECIBIDOCONSUBANCO   / 0126852430  140 1847433K"
- Monto: $366.00
- Referencia: 0126852430


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
  "categoria": "Transferencia Entre Cuentas",
  "cuenta_vinculada": "TDB UBER PRO CONSUBANCO",
  "nota_ia": "El movimiento contiene 'SPEI RECIBIDOCONSUBANCO', lo que indica una transferencia entrante desde CONSUBANCO.",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI", "Transferencia Entre Cuentas"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia Entre Cuentas",
  "cuenta_vinculada": "TDB UBER PRO CONSUBANCO",
  "nota_ia": "El movimiento contiene 'SPEI RECIBIDOCONSUBANCO', lo que indica una transferencia entrante desde CON",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI",
    "Transferencia Entre Cuentas"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Transferencia Entre Cuentas  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: TDB UBER PRO CONSUBANCO

---

## Movimiento #43
**Fecha**: 2025-07-08  
**Descripción**: `SPEI RECIBIDOSPIN BY OXXO / 0126848795  728 0667421k`  
**Monto**: $40.00  
**Tiempo respuesta**: 10.53s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-08
- Descripción original: "SPEI RECIBIDOSPIN BY OXXO / 0126848795  728 0667421k"
- Monto: $40.00
- Referencia: 0126848795


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos ISP
- Ingresos Rent...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": "TDB SPIN OXXO 2113",
  "nota_ia": "Movimiento identificado como transferencia SPEI recibida desde OXXO, vinculada a la cuenta TDB SPIN OXXO 2113.",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI", "TDB SPIN OXXO 2113"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": "TDB SPIN OXXO 2113",
  "nota_ia": "Movimiento identificado como transferencia SPEI recibida desde OXXO, vinculada a la cuenta TDB SPIN ",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI",
    "TDB SPIN OXXO 2113"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Transferencia SPEI  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: TDB SPIN OXXO 2113

---

## Movimiento #44
**Fecha**: 2025-07-08  
**Descripción**: `PAGO CUENTA DE TERCERO    /  0049634135     BNET    0194446569 Prestamo`  
**Monto**: $22,000.00  
**Tiempo respuesta**: 10.30s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-08
- Descripción original: "PAGO CUENTA DE TERCERO    /  0049634135     BNET    0194446569 Prestamo"
- Monto: $22,000.00
- Referencia: 0049634135


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
  "tipo": "GASTO",
  "categoria": "Pago de Prestamo",
  "cuenta_vinculada": "PRESTAMOS REFIN25",
  "nota_ia": "El movimiento corresponde a un pago de préstamo, identificado por la descripción 'Prestamo' y la referencia numérica.",
  "confianza": 0.95,
  "reglas_aplicadas": ["Descripción contiene 'Prestamo'", "Monto negativo indica salida de dinero"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "GASTO",
  "categoria": "Pago de Prestamo",
  "cuenta_vinculada": "PRESTAMOS REFIN25",
  "nota_ia": "El movimiento corresponde a un pago de préstamo, identificado por la descripción 'Prestamo' y la ref",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "Descripción contiene 'Prestamo'",
    "Monto negativo indica salida de dinero"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: GASTO
- ✅ **Categoría**: Pago de Prestamo  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: PRESTAMOS REFIN25

---

## Movimiento #45
**Fecha**: 2025-07-05  
**Descripción**: `SPEI RECIBIDOSANTANDER    / 0113433647  014 9048460TRANSFERENCIA A ABELARDO INTER`  
**Monto**: $270.00  
**Tiempo respuesta**: 9.42s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-05
- Descripción original: "SPEI RECIBIDOSANTANDER    / 0113433647  014 9048460TRANSFERENCIA A ABELARDO INTER"
- Monto: $270.00
- Referencia: 0113433647


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia Entre Cuentas",
  "cuenta_vinculada": null,
  "nota_ia": "Movimiento identificado como transferencia por contener 'SPEI' y 'TRANSFERENCIA' en la descripción.",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI", "TRANSF"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia Entre Cuentas",
  "cuenta_vinculada": null,
  "nota_ia": "Movimiento identificado como transferencia por contener 'SPEI' y 'TRANSFERENCIA' en la descripción.",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI",
    "TRANSF"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Transferencia Entre Cuentas  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: None

---

## Movimiento #46
**Fecha**: 2025-07-04  
**Descripción**: `SPEI RECIBIDOBANORTE      / 0105556429  072 0250704pago`  
**Monto**: $270.00  
**Tiempo respuesta**: 9.05s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-04
- Descripción original: "SPEI RECIBIDOBANORTE      / 0105556429  072 0250704pago"
- Monto: $270.00
- Referencia: 0105556429


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos ISP
- Ingresos ...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": "TDB BANORTE 3172",
  "nota_ia": "Movimiento identificado como transferencia SPEI recibida desde Banorte.",
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
  "nota_ia": "Movimiento identificado como transferencia SPEI recibida desde Banorte.",
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

## Movimiento #47
**Fecha**: 2025-07-04  
**Descripción**: `SAT                       / GUIA:6211617    REF:04254ITE630046581229 CIE:0844985`  
**Monto**: $-1,682.00  
**Tiempo respuesta**: 11.07s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-04
- Descripción original: "SAT                       / GUIA:6211617    REF:04254ITE630046581229 CIE:0844985"
- Monto: $-1,682.00
- Referencia: 6300465812


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 14...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "GASTO",
  "categoria": "Impuestos/Servicios",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un pago al SAT (Servicio de Administración Tributaria), indicado por la descripción 'SAT' y la referencia con formato de documento fiscal.",
  "confianza": 0.95,
  "reglas_aplicadas": ["monto negativo en cuenta BBVA", "descripción con entidad gubernamental (SAT)"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "GASTO",
  "categoria": "Impuestos/Servicios",
  "cuenta_vinculada": null,
  "nota_ia": "El movimiento corresponde a un pago al SAT (Servicio de Administración Tributaria), indicado por la ",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "monto negativo en cuenta BBVA",
    "descripción con entidad gubernamental (SAT)"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: GASTO
- ✅ **Categoría**: Impuestos/Servicios  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: None

---

## Movimiento #48
**Fecha**: 2025-07-03  
**Descripción**: `SPEI RECIBIDOSANTANDER    / 0100128207  014 44364050307`  
**Monto**: $19,720.00  
**Tiempo respuesta**: 9.83s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-03
- Descripción original: "SPEI RECIBIDOSANTANDER    / 0100128207  014 44364050307"
- Monto: $19,720.00
- Referencia: 0100128207


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
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": null,
  "nota_ia": "Movimiento identificado como transferencia SPEI recibida desde Santander, pero no se especifica cuenta destino en BBVA.",
  "confianza": 0.90,
  "reglas_aplicadas": ["SPEI", "nombres bancarios"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencia SPEI",
  "cuenta_vinculada": null,
  "nota_ia": "Movimiento identificado como transferencia SPEI recibida desde Santander, pero no se especifica cuen",
  "confianza": 0.9,
  "reglas_aplicadas": [
    "SPEI",
    "nombres bancarios"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Transferencia SPEI  
- ✅ **Confianza**: 0.9
- ✅ **Cuenta vinculada**: None

---

## Movimiento #49
**Fecha**: 2025-07-02  
**Descripción**: `PAGO CUENTA DE TERCERO    /  0011778300     BNET    2767356773 depos junio 2025`  
**Monto**: $670.00  
**Tiempo respuesta**: 10.18s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-02
- Descripción original: "PAGO CUENTA DE TERCERO    /  0011778300     BNET    2767356773 depos junio 2025"
- Monto: $670.00
- Referencia: 0011778300


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- ...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "GASTO",
  "categoria": "Servicios Básicos",
  "cuenta_vinculada": null,
  "nota_ia": "Pago a cuenta de tercero descrito como 'depos junio 2025', probablemente relacionado con servicios básicos o mantenimiento.",
  "confianza": 0.85,
  "reglas_aplicadas": ["Salida de dinero hacia servicios/productos/proveedores"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "GASTO",
  "categoria": "Servicios Básicos",
  "cuenta_vinculada": null,
  "nota_ia": "Pago a cuenta de tercero descrito como 'depos junio 2025', probablemente relacionado con servicios b",
  "confianza": 0.85,
  "reglas_aplicadas": [
    "Salida de dinero hacia servicios/productos/proveedores"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: GASTO
- ✅ **Categoría**: Servicios Básicos  
- ✅ **Confianza**: 0.85
- ✅ **Cuenta vinculada**: None

---

## Movimiento #50
**Fecha**: 2025-07-01  
**Descripción**: `SPEI ENVIADO Mercado Pago / 0091397656  722 0906250ok`  
**Monto**: $-6,200.00  
**Tiempo respuesta**: 10.33s  

### Prompt Enviado:
```
Eres un experto contable especializado en clasificación financiera BBVA.

MOVIMIENTO BANCARIO:
- Fecha: 2025-07-01
- Descripción original: "SPEI ENVIADO Mercado Pago / 0091397656  722 0906250ok"
- Monto: $-6,200.00
- Referencia: 0091397656


CUENTAS CONOCIDAS EN EL SISTEMA:
- COMPRAS PROYECTO 180 FIBRA
- COTO 4 AC COLONOS SANTANDER MTTO Y MULTAS
- CREDITO HIPOTECA CASA 142
- CTA DEBITO EFECTIVO
- Comisiones Bancarias
- Compra comida en la calle
- INGRESOS RENTA CASA 142
- Ingresos ISP
- Ingresos...
```

### Respuesta Raw de DeepSeek:
```json
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencias Entre Cuentas",
  "cuenta_vinculada": "TDB MPAGO 6007",
  "nota_ia": "El movimiento es un SPEI enviado a Mercado Pago, lo que indica una transferencia a otra cuenta propia.",
  "confianza": 0.95,
  "reglas_aplicadas": ["SPEI", "Transferencias Entre Cuentas"]
}
```
```

### Respuesta Procesada:
```json
{
  "tipo": "TRANSFERENCIA",
  "categoria": "Transferencias Entre Cuentas",
  "cuenta_vinculada": "TDB MPAGO 6007",
  "nota_ia": "El movimiento es un SPEI enviado a Mercado Pago, lo que indica una transferencia a otra cuenta propi",
  "confianza": 0.95,
  "reglas_aplicadas": [
    "SPEI",
    "Transferencias Entre Cuentas"
  ]
}
```

### Evaluación:
- ✅ **Tipo detectado**: TRANSFERENCIA
- ✅ **Categoría**: Transferencias Entre Cuentas  
- ✅ **Confianza**: 0.95
- ✅ **Cuenta vinculada**: TDB MPAGO 6007

---

