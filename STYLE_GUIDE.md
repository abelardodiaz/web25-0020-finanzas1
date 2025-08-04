# Guía de Estilos - Web25-0020-Finanzas1

## Paleta de Colores
### Modo Claro
- Primario: `#3b82f6` (azul)
- Secundario: `#10b981` (verde)
- Fondo: `#f9fafb`
- Tarjetas: `#ffffff`
- Texto: `#1f2937`
- Bordes: `#e5e7eb`

### Modo Oscuro
- Primario: `#60a5fa` (azul claro)
- Secundario: `#34d399` (verde claro)
- Fondo: `#111827`
- Tarjetas: `#1f2937`
- Texto: `#f3f4f6`
- Bordes: `#374151`

## Tipografía
- Familia: `font-sans` (system UI)
- Tamaños:
  - Base: `text-base` (1rem)
  - Títulos: `text-2xl`, `text-3xl`, `text-4xl`
  - Texto pequeño: `text-sm`

## Componentes

### Botones
```html
<!-- Botón Primario con icono -->
<a href="#" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md flex items-center text-lg">
    <i class="fas fa-plus-circle mr-2"></i>Texto
</a>

<!-- Botón Secundario con icono -->
<a href="#" class="px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-md flex items-center text-lg">
    <i class="fas fa-times mr-2"></i>Texto
</a>

<!-- Botones de Acción (Editar/Eliminar) -->
<div class="flex justify-end space-x-2">
    <a href="#" class="text-yellow-600 hover:text-yellow-900 dark:text-yellow-400 dark:hover:text-yellow-300 text-lg" title="Editar">
        <i class="fas fa-edit"></i>
    </a>
    <a href="#" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300 text-lg" title="Eliminar">
        <i class="fas fa-trash"></i>
    </a>
</div>
```

### Tarjetas
```html
<div class="card">
    <!-- Contenido -->
</div>
```

### Formularios
```html
<!-- Contenedor de Formulario -->
<form class="bg-gray-50 dark:bg-gray-800 rounded-lg shadow p-4">
    <!-- Grupo de Campos -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Campo Individual -->
        <div>
            <label class="block text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
                Etiqueta
            </label>
            <input type="text" class="text-lg py-2 px-3 w-full rounded border border-gray-300 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500" placeholder="Ejemplo">
        </div>
    </div>
    
    <!-- Botones de Formulario -->
    <div class="mt-6 flex space-x-3">
        <button type="submit" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md flex items-center text-lg">
            <i class="fas fa-save mr-2"></i>Guardar
        </button>
        <a href="#" class="px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-md flex items-center text-lg">
            <i class="fas fa-times mr-2"></i>Cancelar
        </a>
    </div>
</form>
```

### Tablas

#### Estilo 1: Listado Compacto (estilo_Cuentas)
```html
<div class="overflow-x-auto flex justify-center">
    <table class="table-auto divide-y divide-border">
        <thead class="bg-card">
            <tr>
                <th class="px-4 py-3 text-left">Encabezado</th>
            </tr>
        </thead>
        <tbody class="divide-y divide-border">
            <tr class="hover:bg-card/50">
                <td class="px-4 py-3">Contenido</td>
            </tr>
        </tbody>
    </table>
</div>
```

**Características:**
- Centrado en pantallas grandes (`flex justify-center`)
- Ancho automático de columnas (`table-auto`)
- Padding moderado (`px-4 py-3`)
- Ideal para listados con pocas columnas (3-5)

#### Estilo 2: Tabla Completa (estilo_Transacciones)
```html
<div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-border">
        <thead class="bg-card">
            <tr>
                <th class="px-6 py-4 text-left">Encabezado</th>
            </tr>
        </thead>
        <tbody class="divide-y divide-border">
            <tr class="hover:bg-card/50">
                <td class="px-6 py-4">Contenido</td>
            </tr>
        </tbody>
    </table>
</div>
```

**Características:**
- Ancho completo (`min-w-full`)
- Mayor padding (`px-6 py-4`)
- Scroll horizontal en dispositivos pequeños (`overflow-x-auto`)
- Ideal para tablas con muchas columnas o datos complejos

#### Reglas de uso:
1. **Listados simples** (categorías, cuentas, tipos): Usar **Estilo 1**
2. **Datos complejos** (transacciones, movimientos): Usar **Estilo 2**
3. **Encabezados:** Siempre usar `bg-card` y `text-left`
4. **Filas:** Alternancia con `divide-y divide-border` y hover `hover:bg-card/50`
5. **Responsive:** Contenedor con `overflow-x-auto` para scroll horizontal en móviles

### Tamaños de Fuente
- Texto base: `text-lg` (1.125rem / 18px)
- Títulos: `text-2xl` (1.5rem / 24px) para h3, `text-3xl` para h2, etc.
- Texto pequeño: `text-sm` (0.875rem / 14px)

### Paginación
```html
<!-- Contenedor principal -->
<div class="mt-6 flex flex-col md:flex-row justify-center items-center space-y-4 md:space-y-0 md:space-x-4">
    <!-- Selector de items por página -->
    <form method="get" class="flex items-center">
        <label for="paginate_by" class="text-lg mr-2">Mostrar:</label>
        <select name="paginate_by" class="text-lg rounded border-gray-300 py-1 px-2 bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200" onchange="this.form.submit()">
            <option value="10">10</option>
            <option value="50">50</option>
            <option value="100">100</option>
            <option value="0">Todas</option>
        </select>
    </form>
    
    <!-- Navegación de páginas -->
    <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
        <!-- Primera página -->
        <a href="?page=1" class="relative inline-flex items-center px-3 py-2 rounded-l-md border border-gray-300 bg-gray-50 dark:bg-gray-800 text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
            <span class="sr-only">Primera</span>
            <i class="fas fa-angle-double-left"></i>
        </a>
        
        <!-- Página anterior -->
        <a href="?page={{ previous_page }}" class="relative inline-flex items-center px-3 py-2 border border-gray-300 bg-gray-50 dark:bg-gray-800 text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
            <span class="sr-only">Anterior</span>
            <i class="fas fa-chevron-left"></i>
        </a>
        
        <!-- Indicador de página actual -->
        <span class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-gray-50 dark:bg-gray-800 text-lg font-medium text-gray-700 dark:text-gray-300">
            Página {{ current_page }} de {{ total_pages }}
        </span>
        
        <!-- Página siguiente -->
        <a href="?page={{ next_page }}" class="relative inline-flex items-center px-3 py-2 border border-gray-300 bg-gray-50 dark:bg-gray-800 text-lg font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
            <span class="sr-only">Siguiente</span>
            <i class="fas fa-chevron-right"></i>
        </a>
        
        <!-- Última página -->
        <a href="?page={{ last_page }}" class="relative inline-flex items-center px-3 py-2 rounded-r-md border border-gray-300 bg-gray-50 dark:bg-gray-800 text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
            <span class="sr-only">Última</span>
            <i class="fas fa-angle-double-right"></i>
        </a>
    </nav>
</div>
```

### Características de la Paginación
- **Diseño Responsive:** Se adapta a móviles (columna) y escritorio (fila)
- **Modo Claro/Oscuro:** Colores adaptados para ambos temas
- **Iconos Intuitivos:** Flechas para navegación
- **Selector de Items:** Permite cambiar la cantidad de elementos por página
- **Indicador de Página:** Muestra claramente la página actual y el total

### Notificaciones Toast
```html
<!-- Contenedor de Toasts (se coloca en la parte inferior derecha) -->
<div id="toastContainer" class="fixed bottom-4 right-4 z-50 flex flex-col items-end"></div>

<!-- Ejemplo de Toast (se genera dinámicamente) -->
<div class="px-4 py-3 rounded-md shadow-lg mb-2 flex items-center text-lg bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100">
    <i class="fas fa-check-circle mr-2"></i>
    Mensaje de éxito
</div>

<!-- Script para mostrar toasts -->
<script>
    function showToast(message, type) {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        
        // Clases base
        toast.className = `px-4 py-3 rounded-md shadow-lg mb-2 flex items-center text-lg ${
            type === 'success' 
                ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100' 
                : 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100'
        }`;
        
        // Icono según el tipo
        const iconClass = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';
        toast.innerHTML = `
            <i class="fas ${iconClass} mr-2"></i>
            ${message}
        `;
        
        container.appendChild(toast);
        
        // Auto-eliminar después de 5 segundos
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }
</script>
```

#### Características:
- **Posición:** Fijo en la esquina inferior derecha
- **Colores:**
  - Éxito: Verde claro (fondo) y verde oscuro (texto) en modo claro; verde oscuro (fondo) y verde claro (texto) en modo oscuro
  - Error: Rojo claro (fondo) y rojo oscuro (texto) en modo claro; rojo oscuro (fondo) y rojo claro (texto) en modo oscuro
- **Iconos:** Se muestra un icono diferente para éxito (check) y error (exclamación)
- **Duración:** Se auto-elimina después de 5 segundos
- **Múltiples:** Pueden mostrarse varios toasts a la vez, apilados verticalmente

#### Uso:
1. Coloca el contenedor de toasts (`<div id="toastContainer">`) en la plantilla base (base.html) para que esté disponible en toda la aplicación.
2. Llama a la función `showToast(mensaje, tipo)` con:
   - `mensaje`: El texto a mostrar
   - `tipo`: 'success' para éxito, 'error' para error
```

Este sistema

## Reglas de Implementación
1. **Solo Tailwind**: No usar estilos CSS personalizados fuera de `styles.css`
2. **Variables CSS**: Usar siempre las variables definidas para colores
3. **Responsive**: Usar prefijos responsive (`sm:`, `md:`, `lg:`)
4. **Modo Oscuro**: Usar prefijos `dark:` para estilos específicos
5. **Consistencia**: Reutilizar los componentes definidos 