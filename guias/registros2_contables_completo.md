
# 📒 Registros contables - Ejemplos y clasificación

Este documento muestra cómo registrar operaciones siguiendo el principio de partida doble, clasificando las transacciones y entendiendo las naturalezas de las cuentas.

---

## 🧠 Conceptos básicos

**Naturaleza Deudora**: Su saldo normal es positivo cuando hay más **cargos** (ej. activos, gastos).  
**Naturaleza Acreedora**: Su saldo normal es positivo cuando hay más **abonos** (ej. ingresos, pasivos).

### ✅ Ejemplos con tus cuentas

| Cuenta                                | Tipo     | Naturaleza | ¿Cómo aumenta? | ¿Cómo disminuye? |
|---------------------------------------|----------|------------|----------------|------------------|
| Cuenta de débito en el banco          | Activo   | Deudora    | Cargo          | Abono            |
| Efectivo (si lo manejas también)      | Activo   | Deudora    | Cargo          | Abono            |
| Tarjeta de crédito                    | Pasivo   | Acreedora  | Abono (gastas) | Cargo (pagas)    |
| Renta de casa (lo que te pagan)       | Ingreso  | Acreedora  | Abono          | Cargo (raro)     |
| Gastos de entretenimiento (Netflix)  | Gasto    | Deudora    | Cargo          | Abono (raro)     |
| Gastos de servicios (luz, agua)       | Gasto    | Deudora    | Cargo          | Abono (raro)     |

---

## 🧾 Ejemplos de asientos contables

Cada caso incluye: cuenta origen, cuenta destino, naturaleza y movimientos.

### 1) Pago electricidad con tarjeta de débito ($100)
- **Cuenta origen**: Cuenta de débito — Activo — Deudora — Disminuye → **Abono**
- **Cuenta destino**: Gasto de servicios — Gasto — Deudora — Aumenta → **Cargo**

| Cuenta           | Naturaleza | Movimiento | Monto |
|------------------|------------|------------|-------|
| Gasto de servicios | Deudora   | Cargo      | 100   |
| Cuenta de débito   | Deudora   | Abono      | 100   |

📌 *Se carga la cuenta de gasto porque se incurre en un gasto, y se abona la cuenta de débito porque disminuye el dinero.*

---

### 2) Pago Netflix con tarjeta de crédito ($200)
- **Cuenta origen**: Tarjeta de crédito — Pasivo — Acreedora — Aumenta → **Abono**
- **Cuenta destino**: Gasto de entretenimiento — Gasto — Deudora — Aumenta → **Cargo**

| Cuenta                  | Naturaleza | Movimiento | Monto |
|-------------------------|------------|------------|-------|
| Gasto de entretenimiento | Deudora   | Cargo      | 200   |
| Tarjeta de crédito       | Acreedora | Abono      | 200   |

📌 *Se carga el gasto, se abona la tarjeta porque ahora debes más.*

---

### 3) Pago de tarjeta de crédito con tarjeta de débito ($300)
- **Cuenta origen**: Tarjeta de crédito — Pasivo — Acreedora — Disminuye → **Cargo**
- **Cuenta destino**: Cuenta de débito — Activo — Deudora — Disminuye → **Abono**

| Cuenta           | Naturaleza | Movimiento | Monto |
|------------------|------------|------------|-------|
| Tarjeta de crédito | Acreedora | Cargo      | 300   |
| Cuenta de débito   | Deudora   | Abono      | 300   |

📌 *Pagas la deuda, por eso la tarjeta se carga (baja saldo deudor) y tu cuenta de débito se abona (sale dinero).*

---

### 4) Registro ingreso en cuenta de débito por renta de casa ($1000)
- **Cuenta origen**: Cuenta de débito — Activo — Deudora — Aumenta → **Cargo**
- **Cuenta destino**: Ingreso por renta — Ingreso — Acreedora — Aumenta → **Abono**

| Cuenta           | Naturaleza | Movimiento | Monto  |
|------------------|------------|------------|--------|
| Cuenta de débito | Deudora    | Cargo      | 1000   |
| Ingreso por renta| Acreedora  | Abono      | 1000   |

📌 *La cuenta de débito aumenta (cargo) y el ingreso aumenta (abono).*

---

## 📊 Clasificación por tipo de transacción

1. **Ingreso**  
   - Entrada de dinero desde una fuente externa (cliente, inquilino, venta).
   - Criterio: una cuenta de medio de pago aumenta y la otra es de resultado (Ingreso).

2. **Gasto**  
   - Salida de dinero hacia un proveedor o servicio.
   - Criterio: una cuenta de medio de pago disminuye y la otra es de resultado (Gasto).

3. **Transferencia interna**  
   - Movimiento entre dos cuentas que son medios de pago (por ejemplo, débito → efectivo).
   - Criterio: ambas cuentas involucradas son medios de pago.

💡 **Identificación en un sistema**: marcar las cuentas con `es_medio_pago = true` para facilitar esta clasificación.

---

## 📂 Clasificación de cuentas: Medios de pago vs. Cuentas de resultado

### 1️⃣ Cuentas de movimientos reales de dinero (Medios de pago o almacenamiento de fondos)
- Representan activos líquidos (dinero disponible) o pasivos exigibles (deudas).
- Ejemplos:
  - **Activo**: Efectivo, Caja chica, Cuenta de débito, Cuenta de ahorros, PayPal.
  - **Pasivo**: Tarjeta de crédito, préstamo bancario.
- Características:
  - Se pueden usar para pagar o recibir dinero.
  - Posible hacer **transferencias internas** entre ellas.

💡 En un sistema: `es_medio_pago = true`.

---

### 2️⃣ Cuentas de resultado (Ingresos y Gastos)
- No representan dinero físico; son categorías de registro de operaciones.
- Ejemplos:
  - Ingresos por renta, Ingresos por servicios técnicos.
  - Gastos de electricidad, Gastos de entretenimiento, Gastos de mantenimiento.
- Características:
  - No se transfieren entre ellas.
  - Miden desempeño económico.

💡 En un sistema: `es_medio_pago = false` y `tipo = gasto` o `tipo = ingreso`.

---

### 📋 Tabla de identificación rápida

| Código | Nombre                      | Naturaleza | Tipo contable   | ¿Medio de pago? |
|--------|-----------------------------|------------|-----------------|-----------------|
| DEB    | Cuenta de débito            | Deudora    | Activo          | Sí              |
| EFE    | Efectivo                    | Deudora    | Activo          | Sí              |
| TDC    | Tarjeta de crédito          | Acreedora  | Pasivo          | Sí              |
| RENTA  | Ingreso por renta           | Acreedora  | Ingreso         | No              |
| SERV   | Gasto de servicios          | Deudora    | Gasto           | No              |
| ENT    | Gasto de entretenimiento    | Deudora    | Gasto           | No              |
| SOPTEC | Ingreso por soporte técnico | Acreedora  | Ingreso         | No              |

---

### 📌 Analogía
- **Medios de pago** = bolsillos, cuentas y tarjetas donde mueves dinero real.
- **Cuentas de resultado** = etiquetas para clasificar de dónde vino o a dónde se fue el dinero.

---

### 🏛 Clasificación contable clásica
- Medios de pago → **Cuentas de balance** (Activo o Pasivo).
- Ingresos/Gastos → **Cuentas de resultados** (Estado de pérdidas y ganancias).

