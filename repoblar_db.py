#!/usr/bin/env python3
"""
Script para repoblar la base de datos con datos iniciales
Uso: python repoblar_db.py
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    """Repoblar base de datos con datos iniciales"""
    
    # Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    print("🚀 Iniciando repoblación de la base de datos...")
    
    try:
        # 1. Cargar tipos de cuenta y categorías
        print("📂 Cargando tipos de cuenta y categorías...")
        execute_from_command_line([
            'manage.py', 'loaddata', 
            'core/fixtures/datos_iniciales_completos.json'
        ])
        print("✅ Tipos de cuenta y categorías cargados exitosamente")
        
        # 2. Cargar cuentas de ejemplo
        print("🏦 Cargando cuentas de ejemplo...")
        execute_from_command_line([
            'manage.py', 'loaddata', 
            'core/fixtures/cuenta_bbva_ejemplo.json'
        ])
        print("✅ Cuentas de ejemplo cargadas exitosamente")
        
        print("\n🎉 ¡Base de datos repoblada exitosamente!")
        print("\n📊 Datos cargados:")
        print("   - 18 tipos de cuenta")
        print("   - 44 categorías (personal y negocio)")
        print("   - 3 cuentas de ejemplo (incluye BBVA 5019)")
        
        print("\n🌐 URLs disponibles:")
        print("   - http://localhost:8299/bbva/           - Sistema BBVA")
        print("   - http://localhost:8299/conciliacion/  - Conciliación")
        print("   - http://localhost:8299/cuentas/       - Gestión de cuentas")
        print("   - http://localhost:8299/               - Dashboard")
        
    except Exception as e:
        print(f"❌ Error durante la repoblación: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()