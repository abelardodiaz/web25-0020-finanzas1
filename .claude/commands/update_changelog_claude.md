"""
🚀 PROMPT TEMPLATE: Automatic Changelog Generator

Copy and use this prompt to ask Claude to update the changelog automatically:

---

PROMPT FOR CLAUDE:
==================

Actualiza el archivo `changelog_claude.md` en la raíz del proyecto con los cambios realizados hoy. 


🎯 **Objetivo**: ser organizado en la documentación de cambios.

📋 **Formato Markdown Avanzado:**
- Usa emojis temáticos para cada sección (🎨 UI, 🔧 Fixes, 🚀 Features, 📚 Docs, etc.)
- Organiza por categorías lógicas y visualmente atractivas
- Incluye subsecciones con bullets descriptivos
- Agrega checkmarks ✅ para completado, 🔄 para en progreso
- Usa badges/indicadores de impacto: `HIGH`, `MEDIUM`, `LOW`

🗓️ **Estructura Temporal:**
- Agregar nueva sección con fecha de hoy en formato `## 🗓️ DD de Mes, YYYY`
- Mantener orden cronológico descendente (más reciente arriba)
- Agrupar cambios por contexto/módulo cuando sea relevante

🎨 **Estilo Creativo:**
- Títulos descriptivos y atractivos (no solo "Fixed bug")
- Explicaciones técnicas pero accesibles
- URLs/rutas afectadas claramente identificadas
- Impacto del cambio en la experiencia del usuario
- Referencias a archivos específicos con formato `file:line`

📊 **Métricas de Impacto:**
- Conteo de archivos modificados
- URLs afectadas
- Funcionalidades mejoradas/agregadas
- Errores corregidos

🔗 **Context Awareness:**
- Analiza el repositorio para entender qué cambios se hicieron
- Infiere el propósito y beneficio de cada cambio
- Conecta cambios relacionados en una narrativa coherente

🎭 **Tono y Personalidad:**
- Profesional pero con personalidad
- Celebra los logros con entusiasmo apropiado
- Transparente sobre problemas resueltos
- Orientado al valor para el usuario final

**EJEMPLO DE OUTPUT ESPERADO:**

```markdown
## 🗓️ DD de Mes, 2025

### 🎨 **Frontend Revolution** `HIGH IMPACT`
#### ✨ **Component Modernization**
- **🚀 Enhanced:** `components/UserDashboard.tsx`
  - ✅ Migrated from legacy CSS to Tailwind utilities
  - ✅ Added responsive breakpoints for mobile-first design
  - ✅ Implemented accessibility improvements (ARIA labels)
  - 📈 **Impact:** 40% faster load times, improved mobile UX

### 🔧 **Critical Fixes** `HIGH IMPACT`
- **🐛 Resolved:** Authentication timeout issue in `auth/middleware.py:45`
  - Fixed session expiration handling
  - Added graceful fallback for expired tokens
  - 🎯 **Affected:** All authenticated routes
```

**REGLAS ESPECÍFICAS:**
1. NO sobrescribir el contenido existente
2. SIEMPRE agregar al principio (después del header)
3. SER ESPECÍFICO con números de línea cuando sea relevante
4. INCLUIR métricas cuantificables cuando sea posible
5. MANTENER consistencia con el estilo establecido
6. USAR formato de fecha en español
7. AGREGAR footer con timestamp de generación

---


"""