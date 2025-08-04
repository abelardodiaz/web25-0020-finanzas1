
# Registro Contable con Doble Partida

Este archivo contiene ejemplos prácticos de cómo registrar transacciones financieras siguiendo el principio contable de la **doble partida**. Incluye la clasificación de cuentas, naturaleza deudora o acreedora, así como ejemplos con cargos y abonos.

---

## 🧠 ¿Qué significa "deudora" y "acreedora"?

- **Deudora**: su saldo normal es positivo cuando hay más **cargos** (ej. activos, gastos).
- **Acreedora**: su saldo normal es positivo cuando hay más **abonos** (ej. ingresos, pasivos).

---

## ✅ Ejemplos con tus cuentas

| Cuenta                             | Tipo       | Naturaleza | ¿Cómo aumenta? | ¿Cómo disminuye? |
|------------------------------------|------------|------------|----------------|------------------|
| Cuenta de débito en el banco       | Activo     | Deudora    | Cargo          | Abono            |
| Efectivo (si lo manejas también)   | Activo     | Deudora    | Cargo          | Abono            |
| Tarjeta de crédito                 | Pasivo     | Acreedora  | Abono (gastas) | Cargo (pagas)    |
| Renta de casa (lo que te pagan)    | Ingreso    | Acreedora  | Abono          | Cargo (raro)     |
| Gastos de entretenimiento (Netflix)| Gasto      | Deudora    | Cargo          | Abono (raro)     |
| Gastos de servicios (luz, agua)    | Gasto      | Deudora    | Cargo          | Abono            |

---

## 🔍 Clasificación de transacciones

### 1. Ingreso
- Implica el aumento de dinero en una cuenta (activo) a cambio de un ingreso (acreedor).
- Ejemplo: recibir dinero por renta.

### 2. Gasto
- Implica una disminución de dinero o aumento de deuda, a cambio de un gasto registrado.
- Ejemplo: pagar Netflix o electricidad.

### 3. Transferencia interna
- Mueve dinero entre dos **medios de pago** (activos o pasivos), sin generar ingreso ni gasto.
- Ejemplo: pagar tarjeta de crédito con cuenta de débito.

💡 **Tip para detectar transferencias**: Si ambas cuentas involucradas son medios de pago (cuenta bancaria, tarjeta, efectivo), y no hay ingreso ni gasto relacionado, es una transferencia.

---

## 📘 Ejemplos con doble partida

### 1. Pago electricidad con tarjeta de débito $100
- Tipo: **Gasto**
- Cuenta origen: Cuenta de débito (Activo, Deudora)
- Cuenta destino: Gasto de servicios (Gasto, Deudora)

| Cuenta               | Cargo | Abono |
|----------------------|-------|-------|
| Gasto de servicios   | 100   |       |
| Cuenta de débito     |       | 100   |

➡️ Se carga el gasto porque aumenta, y se abona la cuenta de débito porque disminuye.

---

### 2. Pago Netflix con tarjeta de crédito $200
- Tipo: **Gasto**
- Cuenta origen: Tarjeta de crédito (Pasivo, Acreedora)
- Cuenta destino: Gasto de entretenimiento (Gasto, Deudora)

| Cuenta                      | Cargo | Abono |
|-----------------------------|-------|-------|
| Gasto de entretenimiento    | 200   |       |
| Tarjeta de crédito          |       | 200   |

➡️ Se carga el gasto porque aumenta, y se abona la tarjeta porque aumenta la deuda.

---

### 3. Pago tarjeta de crédito con tarjeta de débito $300
- Tipo: **Transferencia interna**
- Cuenta origen: Cuenta de débito (Activo, Deudora)
- Cuenta destino: Tarjeta de crédito (Pasivo, Acreedora)

| Cuenta               | Cargo | Abono |
|----------------------|-------|-------|
| Tarjeta de crédito   | 300   |       |
| Cuenta de débito     |       | 300   |

➡️ Se carga la tarjeta (disminuye la deuda), se abona la cuenta de débito (disminuye el activo).

---

### 4. Ingreso de dinero por renta $1000
- Tipo: **Ingreso**
- Cuenta origen: Renta de casa (Ingreso, Acreedora)
- Cuenta destino: Cuenta de débito (Activo, Deudora)

| Cuenta             | Cargo | Abono |
|--------------------|-------|-------|
| Cuenta de débito   | 1000  |       |
| Renta de casa      |       | 1000  |

➡️ Se carga la cuenta de débito (aumenta el activo) y se abona el ingreso (aumenta el ingreso).

---
