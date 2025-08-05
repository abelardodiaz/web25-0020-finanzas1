"""
🚀 PROMPT TEMPLATE: README Update & Git Push

Copy and use this prompt to ask Claude to update README and push to GitHub:

---

PROMPT FOR CLAUDE:
==================

Actualiza el @README.md con todos los cambios del día de hoy. Toma la información del @changelog_claude.md, pero en el README somos menos técnicos y más concretos. 

**INSTRUCCIONES ESPECÍFICAS:**

📋 **Formato y Estructura:**
- Lo último siempre va al **INICIO** del README (después del header)
- Versión: Incrementar la versión (ej. si era 0.5.6, ahora será 0.5.7)
- Estilo: Menos técnico que el changelog, más orientado al usuario final
- Fecha: Usar formato español "DD de Mes, YYYY"

🎯 **Contenido a Incluir:**
- Nuevas funcionalidades implementadas
- Mejoras en la experiencia de usuario
- Correcciones importantes realizadas
- Cambios en la interfaz de usuario
- Optimizaciones de rendimiento

📝 **Estilo de Escritura:**
- Lenguaje claro y directo
- Orientado al beneficio del usuario
- Menos jerga técnica que el changelog
- Emojis para hacer más amigable la lectura
- Bullets concisos pero informativos

🔧 **Proceso Completo:**
1. Leer el changelog_claude.md del día de hoy
2. Extraer los cambios más relevantes para el usuario final
3. Redactar de forma menos técnica y más concreta
4. Agregar la nueva sección AL INICIO del README
5. Incrementar la versión del proyecto
6. Ejecutar los comandos git:
   ```bash
   git add .
   git commit -m "v0.X.X - [RESUMEN DE CAMBIOS PRINCIPALES DEL DÍA]
   
   - [Cambio importante 1]
   - [Cambio importante 2]  
   - [Cambio importante 3]
   - [Otros cambios relevantes]"
   git push
   ```

**EJEMPLO DE OUTPUT README:**

```markdown
## 🗓️ Versión 0.5.7 - DD de Mes, 2025

### ✨ Nuevas Funcionalidades
- 🏦 **Sistema contable profesional:** Implementación completa de doble partida contable
- 🎨 **Interfaz mejorada:** Colores y visualización más clara en estados de cuenta
- 📊 **Separación de columnas:** Cargos y abonos ahora se muestran por separado

### 🔧 Mejoras y Correcciones
- ✅ Corrección en visualización de tarjetas de crédito
- ✅ Lógica contable alineada con estándares bancarios
- ✅ Experiencia de usuario más intuitiva

### 📈 Beneficios para el Usuario
- Mayor precisión en reportes financieros
- Visualización más clara de movimientos
- Compatibilidad con principios contables estándar
```

**REGLAS IMPORTANTES:**
1. SIEMPRE agregar la nueva versión AL INICIO del README
2. SER CONCRETO: enfocar en beneficios del usuario, no en detalles técnicos  
3. USAR LENGUAJE SIMPLE: evitar términos como "implementación", "refactoring", etc.
4. INCLUIR EMOJIS: para hacer más amigable la lectura
5. COMMIT MESSAGE: debe resumir los cambios principales del día
6. VERSION: incrementar automáticamente (ej. 0.5.6 → 0.5.7)

---


"""