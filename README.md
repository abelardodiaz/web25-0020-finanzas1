
#CHANGELOG
# Registro de Cambios - WEB0020-FINANZAS1
## 📊 Sistema de Gestión Financiera



## [0.4.0] - 2025-07-29 - 19:50 hrs

### ✨ Nuevas Funcionalidades

1. **Generación de PDF para estados de cuenta**
   - Botón "Generar PDF" en la vista de detalle de períodos (`/periodos/<id>/`)
   - Formato profesional con columnas separadas para cargos/abonos
   - Totales redondeados a 2 decimales
   - Uso de biblioteca `reportlab` (añadida a requirements.txt)

2. **Sistema de actualización dinámica de listas**
   - Botones de refresh (↻) en formulario de transacciones
   - Actualización AJAX para:
     - Cuentas de servicio
     - Categorías
     - Medios de pago
   - Endpoints JSON:
     - `/transacciones/refresh_cuentas/`
     - `/transacciones/refresh_categorias/`
     - `/transacciones/refresh_medios/`

3. **Mejoras en filtrado de cuentas**
   - Campo "Medio de pago" ahora muestra solo cuentas válidas:
     - Tipos DEB (Débito)
     - Tipos CRE (Crédito)
   - Exclusión de cuentas no aptas (Servicios, Proveedores, etc.)

### 🔧 Mejoras y Optimizaciones

1. **Clarificación de categorías**
   - Modificación del modelo `Categoria`:
     - El método `__str__` ahora incluye tipo (Personal/Negocio)
     - Ej: "Electricidad (Personal)" vs "Electricidad (Negocio)"
   - Elimina ambigüedad en selección de categorías

2. **Gestión de grupos de cuentas**
   - Edición directa del grupo en formulario de cuentas
   - Asignación automática al tipo de cuenta relacionado
   - Validación en tiempo real

3. **Manejo de errores en períodos**
   - Corrección de `PeriodoEstadoLog`:
     - Campo `periodo` añadido como obligatorio
     - Migración segura para datos existentes
     - Script de actualización vía shell de Django

### 🐛 Correcciones de Errores

1. **TypeError en actualización de períodos**
   - Solucionado: `PeriodoEstadoLog() got unexpected keyword arguments: 'periodo'`
   - Implementada relación FK correcta con modelo `Periodo`

2. **Problemas de migración**
   - Manejo seguro de campos no-nulables en migraciones
   - Script para asignar períodos a registros existentes:
     ```bash
     echo "from core.models import PeriodoEstadoLog, Periodo; logs = PeriodoEstadoLog.objects.filter(periodo__isnull=True); periodo = Periodo.objects.first(); logs.update(periodo=periodo)" | python manage.py shell
     ```

3. **Filtrado incorrecto en formularios**
   - Corregido despliegue de cuentas no válidas como medios de pago
   - Optimización de querysets en `TransaccionForm`

### 📦 Dependencias Actualizadas
- Añadida `reportlab==4.1.0` a requirements.txt
- Actualizadas migraciones de base de datos

---

**Notas de Implementación:**
- Los cambios en representación de categorías afectan todos los dropdowns del sistema
- Los endpoints AJAX siguen convenciones RESTful
- Las plantillas actualizadas se encuentran en `templates/transacciones/`
- Las migraciones requieren aplicación secuencial (`makemigrations` + `migrate`)# Registro de Cambios - WEB0020-FINANZAS1

## [0.4.0] - 2025-07-29

### ✨ Nuevas Funcionalidades

1. **Generación de PDF para estados de cuenta**
   - Botón "Generar PDF" en la vista de detalle de períodos (`/periodos/<id>/`)
   - Formato profesional con columnas separadas para cargos/abonos
   - Totales redondeados a 2 decimales
   - Uso de biblioteca `reportlab` (añadida a requirements.txt)

2. **Sistema de actualización dinámica de listas**
   - Botones de refresh (↻) en formulario de transacciones
   - Actualización AJAX para:
     - Cuentas de servicio
     - Categorías
     - Medios de pago
   - Endpoints JSON:
     - `/transacciones/refresh_cuentas/`
     - `/transacciones/refresh_categorias/`
     - `/transacciones/refresh_medios/`

3. **Mejoras en filtrado de cuentas**
   - Campo "Medio de pago" ahora muestra solo cuentas válidas:
     - Tipos DEB (Débito)
     - Tipos CRE (Crédito)
   - Exclusión de cuentas no aptas (Servicios, Proveedores, etc.)

### 🔧 Mejoras y Optimizaciones

1. **Clarificación de categorías**
   - Modificación del modelo `Categoria`:
     - El método `__str__` ahora incluye tipo (Personal/Negocio)
     - Ej: "Electricidad (Personal)" vs "Electricidad (Negocio)"
   - Elimina ambigüedad en selección de categorías

2. **Gestión de grupos de cuentas**
   - Edición directa del grupo en formulario de cuentas
   - Asignación automática al tipo de cuenta relacionado
   - Validación en tiempo real

3. **Manejo de errores en períodos**
   - Corrección de `PeriodoEstadoLog`:
     - Campo `periodo` añadido como obligatorio
     - Migración segura para datos existentes
     - Script de actualización vía shell de Django

### 🐛 Correcciones de Errores

1. **TypeError en actualización de períodos**
   - Solucionado: `PeriodoEstadoLog() got unexpected keyword arguments: 'periodo'`
   - Implementada relación FK correcta con modelo `Periodo`

2. **Problemas de migración**
   - Manejo seguro de campos no-nulables en migraciones
   - Script para asignar períodos a registros existentes:
     ```bash
     echo "from core.models import PeriodoEstadoLog, Periodo; logs = PeriodoEstadoLog.objects.filter(periodo__isnull=True); periodo = Periodo.objects.first(); logs.update(periodo=periodo)" | python manage.py shell
     ```

3. **Filtrado incorrecto en formularios**
   - Corregido despliegue de cuentas no válidas como medios de pago
   - Optimización de querysets en `TransaccionForm`

### 📦 Dependencias Actualizadas
- Añadida `reportlab==4.1.0` a requirements.txt
- Actualizadas migraciones de base de datos

---

**Notas de Implementación:**
- Los cambios en representación de categorías afectan todos los dropdowns del sistema
- Los endpoints AJAX siguen convenciones RESTful
- Las plantillas actualizadas se encuentran en `templates/transacciones/`
- Las migraciones requieren aplicación secuencial (`makemigrations` + `migrate`)

########################
V.0.0.0


## 📊 Sistema de Gestión Financiera

Este proyecto es una herramienta integral para administrar finanzas personales y empresariales. Permite:

### 1. Gestión de Cuentas Bancarias
- Registro de cuentas (débito, crédito, servicios)
- Clasificación por tipo (MXN/USD) y grupo (débito, crédito, servicios)
- Detalles completos: referencias, contratos, fechas de apertura
- Cálculo automático de saldos

### 2. Clasificación de Transacciones
- Categorías jerárquicas (ej: "Alimentos > Supermercado")
- Diferenciación entre gastos personales y de negocio
- Tipos de operaciones: ingresos, gastos y transferencias

### 3. Operaciones Financieras
- Registro detallado de movimientos con fechas y descripciones
- Conciliación bancaria
- Manejo automático de signos (gastos negativos, ingresos positivos)
- Transferencias entre cuentas con registro dual

### 4. Funciones Avanzadas
- **Recurrencias**: Programación de pagos automáticos (ej: servicios mensuales)
- **Generación de recibos**: Sistema para registrar pagos de servicios
- **Periodos de facturación**: Gestión de cortes de tarjetas y servicios con:
  - Fechas de corte y límite de pago
  - Montos totales, mínimos y sin intereses
  - Estados (pendiente/pagado/cancelado)

## 🔄 Procesos Clave
- **Conciliación**: Marcar transacciones verificadas
- **Generación de estados**: Períodos mensuales con resúmenes financieros
- **Jerarquías flexibles**: Categorías y subcategorías ilimitadas
- **Monedas**: Soporte para operaciones en MXN y USD

## 💻 Tecnología Utilizada
- Base de datos segura (MariaDB)
- Entorno configurable para desarrollo/producción
- Sistema modular y escalable

## 📈 Beneficios para la Gestión
- Visión unificada de finanzas personales y empresariales
- Seguimiento preciso de obligaciones y vencimientos
- Clasificación de gastos para análisis presupuestal
- Automatización de pagos recurrentes
- Control de tarjetas de crédito (cortes y pagos)