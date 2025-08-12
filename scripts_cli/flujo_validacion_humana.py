#!/usr/bin/env python3
"""
Flujo de Validación Humana para Aprendizaje de IA
Sistema de retroalimentación y mejora continua
Versión 0.8.5
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Agregar el directorio del proyecto al path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from sistema_memoria import MemoriaPatrones
from deepseek_client import DeepSeekClient, Colors
from detector_patrones import DetectorPatrones

class ValidadorHumano:
    """Sistema de validación humana para mejorar el aprendizaje de IA"""
    
    def __init__(self):
        self.memoria = MemoriaPatrones()
        self.deepseek = DeepSeekClient(test_mode=False)
        self.detector = DetectorPatrones(self.deepseek)
        self.estadisticas = {
            'confirmaciones': 0,
            'correcciones': 0,
            'rechazos': 0,
            'patrones_mejorados': 0
        }
    
    def iniciar_validacion_lote(self, archivo_json: str):
        """Inicia el proceso de validación de un lote de movimientos"""
        print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}")
        print(f"{Colors.BOLD}VALIDADOR HUMANO DE CLASIFICACIONES IA v0.8.5{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}\n")
        
        # Cargar movimientos procesados por IA
        try:
            with open(archivo_json, 'r', encoding='utf-8') as f:
                movimientos = json.load(f)
            print(f"{Colors.OKGREEN}✓ Cargados {len(movimientos)} movimientos{Colors.ENDC}\n")
        except Exception as e:
            print(f"{Colors.FAIL}✗ Error cargando archivo: {e}{Colors.ENDC}")
            return
        
        # Filtrar movimientos con clasificación IA
        movimientos_ia = [m for m in movimientos if 'decision_ia' in m and m['decision_ia']]
        print(f"{Colors.OKCYAN}📊 {len(movimientos_ia)} movimientos con clasificación IA{Colors.ENDC}")
        
        if not movimientos_ia:
            print(f"{Colors.WARNING}No hay movimientos con clasificación IA para validar{Colors.ENDC}")
            return
        
        # Proceso de validación
        for idx, movimiento in enumerate(movimientos_ia, 1):
            print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
            print(f"{Colors.BOLD}Movimiento {idx}/{len(movimientos_ia)}{Colors.ENDC}")
            print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
            
            resultado = self.validar_movimiento(movimiento)
            if resultado == 'exit':
                break
        
        # Mostrar estadísticas finales
        self.mostrar_estadisticas()
        
        # Guardar memoria actualizada
        self.memoria.guardar_memoria()
        print(f"\n{Colors.OKGREEN}✓ Memoria actualizada y guardada{Colors.ENDC}")
    
    def validar_movimiento(self, movimiento: Dict) -> str:
        """Valida un movimiento individual con clasificación IA"""
        # Mostrar información del movimiento
        self.mostrar_movimiento(movimiento)
        
        # Mostrar clasificación IA
        decision_ia = movimiento['decision_ia']
        self.mostrar_clasificacion_ia(decision_ia)
        
        # Solicitar validación
        print(f"\n{Colors.WARNING}VALIDACIÓN HUMANA REQUERIDA:{Colors.ENDC}")
        print("1) ✅ Correcta - La clasificación es precisa")
        print("2) ⚠️  Parcial - Tipo correcto, categoría incorrecta")
        print("3) ❌ Incorrecta - Ambos incorrectos")
        print("4) 🔍 Ver patrones similares en memoria")
        print("5) ⏭️  Saltar este movimiento")
        print("6) 🚪 Salir del validador")
        
        while True:
            opcion = input(f"\n{Colors.OKCYAN}Seleccione opción (1-6): {Colors.ENDC}").strip()
            
            if opcion == '1':
                return self.confirmar_clasificacion(movimiento, decision_ia)
            elif opcion == '2':
                return self.corregir_parcial(movimiento, decision_ia)
            elif opcion == '3':
                return self.corregir_completa(movimiento, decision_ia)
            elif opcion == '4':
                self.mostrar_patrones_similares(movimiento)
            elif opcion == '5':
                print(f"{Colors.WARNING}⏭️  Movimiento saltado{Colors.ENDC}")
                return 'skip'
            elif opcion == '6':
                return 'exit'
            else:
                print(f"{Colors.FAIL}Opción inválida{Colors.ENDC}")
    
    def mostrar_movimiento(self, movimiento: Dict):
        """Muestra información del movimiento"""
        print(f"\n{Colors.OKCYAN}DATOS DEL MOVIMIENTO:{Colors.ENDC}")
        print(f"📅 Fecha: {movimiento.get('fecha', 'N/A')}")
        print(f"📝 Descripción: {movimiento.get('descripcion', 'N/A')}")
        print(f"💰 Monto: ${movimiento.get('monto', 0):,.2f}")
        print(f"🔢 Referencia: {movimiento.get('referencia_bancaria', 'N/A')}")
    
    def mostrar_clasificacion_ia(self, decision_ia: Dict):
        """Muestra la clasificación sugerida por IA"""
        print(f"\n{Colors.OKBLUE}🤖 CLASIFICACIÓN IA:{Colors.ENDC}")
        print(f"📊 Tipo: {Colors.BOLD}{decision_ia.get('tipo', 'N/A')}{Colors.ENDC}")
        print(f"📁 Categoría: {Colors.BOLD}{decision_ia.get('categoria', 'N/A')}{Colors.ENDC}")
        print(f"🏦 Cuenta vinculada: {decision_ia.get('cuenta_vinculada', 'N/A')}")
        print(f"🎯 Confianza: {Colors.BOLD}{decision_ia.get('confianza', 0)*100:.0f}%{Colors.ENDC}")
        print(f"📝 Nota: {decision_ia.get('nota_ia', 'N/A')}")
    
    def confirmar_clasificacion(self, movimiento: Dict, decision_ia: Dict) -> str:
        """Confirma que la clasificación es correcta"""
        # Buscar patrón existente
        patrones = self.memoria.buscar_patrones_existentes(movimiento)
        
        if patrones:
            # Actualizar patrón existente con confirmación
            patron_principal = patrones[0]
            tipo_patron = patron_principal.get('tipo_patron')
            patron_id = movimiento.get('referencia_bancaria') or f"{abs(float(movimiento.get('monto', 0))):.2f}"
            
            feedback = {
                'accion': 'confirmacion',
                'clasificacion_correcta': {
                    'tipo': decision_ia.get('tipo'),
                    'categoria': decision_ia.get('categoria')
                },
                'nota': 'Validado por humano',
                'confianza_usuario': 1.0
            }
            
            self.memoria.registrar_feedback_humano(tipo_patron, patron_id, feedback)
        else:
            # Crear nuevo patrón validado
            patron_def = {
                'tipo': 'referencia' if movimiento.get('referencia_bancaria') else 'monto_exacto',
                'clasificacion_automatica': {
                    'tipo': decision_ia.get('tipo'),
                    'categoria': decision_ia.get('categoria'),
                    'cuenta_vinculada': decision_ia.get('cuenta_vinculada')
                },
                'confianza_patron': 0.90  # Alta confianza por validación humana
            }
            
            self.memoria.registrar_patron_nuevo(patron_def, movimiento, validado_humano=True)
        
        self.estadisticas['confirmaciones'] += 1
        print(f"{Colors.OKGREEN}✓ Clasificación confirmada y registrada en memoria{Colors.ENDC}")
        return 'confirmed'
    
    def corregir_parcial(self, movimiento: Dict, decision_ia: Dict) -> str:
        """Corrige solo la categoría manteniendo el tipo"""
        print(f"\n{Colors.WARNING}CORRECCIÓN PARCIAL:{Colors.ENDC}")
        print(f"Tipo actual: {Colors.BOLD}{decision_ia.get('tipo')}{Colors.ENDC} (se mantendrá)")
        
        categoria_correcta = input(f"{Colors.OKCYAN}Ingrese la categoría correcta: {Colors.ENDC}").strip()
        
        if not categoria_correcta:
            print(f"{Colors.FAIL}Categoría vacía, operación cancelada{Colors.ENDC}")
            return 'cancelled'
        
        # Registrar corrección
        feedback = {
            'accion': 'correccion',
            'clasificacion_original': {
                'tipo': decision_ia.get('tipo'),
                'categoria': decision_ia.get('categoria')
            },
            'clasificacion_correcta': {
                'tipo': decision_ia.get('tipo'),
                'categoria': categoria_correcta
            },
            'nota': 'Corrección parcial: solo categoría'
        }
        
        self.aplicar_correccion(movimiento, feedback)
        self.estadisticas['correcciones'] += 1
        print(f"{Colors.OKGREEN}✓ Corrección parcial registrada{Colors.ENDC}")
        return 'corrected'
    
    def corregir_completa(self, movimiento: Dict, decision_ia: Dict) -> str:
        """Corrige tanto el tipo como la categoría"""
        print(f"\n{Colors.WARNING}CORRECCIÓN COMPLETA:{Colors.ENDC}")
        
        # Seleccionar tipo correcto
        print("\nTipo de transacción:")
        print("1) GASTO")
        print("2) INGRESO")
        print("3) TRANSFERENCIA")
        
        tipo_opcion = input(f"{Colors.OKCYAN}Seleccione tipo (1/2/3): {Colors.ENDC}").strip()
        tipo_map = {'1': 'GASTO', '2': 'INGRESO', '3': 'TRANSFERENCIA'}
        tipo_correcto = tipo_map.get(tipo_opcion)
        
        if not tipo_correcto:
            print(f"{Colors.FAIL}Tipo inválido, operación cancelada{Colors.ENDC}")
            return 'cancelled'
        
        categoria_correcta = input(f"{Colors.OKCYAN}Ingrese la categoría correcta: {Colors.ENDC}").strip()
        
        if not categoria_correcta:
            print(f"{Colors.FAIL}Categoría vacía, operación cancelada{Colors.ENDC}")
            return 'cancelled'
        
        # Registrar corrección completa
        feedback = {
            'accion': 'correccion',
            'clasificacion_original': {
                'tipo': decision_ia.get('tipo'),
                'categoria': decision_ia.get('categoria')
            },
            'clasificacion_correcta': {
                'tipo': tipo_correcto,
                'categoria': categoria_correcta
            },
            'nota': 'Corrección completa: tipo y categoría'
        }
        
        self.aplicar_correccion(movimiento, feedback)
        self.estadisticas['correcciones'] += 1
        print(f"{Colors.OKGREEN}✓ Corrección completa registrada{Colors.ENDC}")
        return 'corrected'
    
    def aplicar_correccion(self, movimiento: Dict, feedback: Dict):
        """Aplica la corrección al sistema de memoria"""
        # Buscar patrón existente
        ref_bancaria = movimiento.get('referencia_bancaria', '')
        monto_str = f"{abs(float(movimiento.get('monto', 0))):.2f}"
        
        if ref_bancaria and ref_bancaria in self.memoria.memoria['patrones_detectados']['referencias_bancarias']:
            self.memoria.registrar_feedback_humano('referencia_bancaria', ref_bancaria, feedback)
            self.estadisticas['patrones_mejorados'] += 1
            
        elif monto_str in self.memoria.memoria['patrones_detectados']['montos_exactos']:
            self.memoria.registrar_feedback_humano('monto_exacto', monto_str, feedback)
            self.estadisticas['patrones_mejorados'] += 1
            
        else:
            # Crear nuevo patrón con la clasificación correcta
            patron_def = {
                'tipo': 'referencia' if ref_bancaria else 'monto_exacto',
                'clasificacion_automatica': feedback['clasificacion_correcta'],
                'confianza_patron': 0.85  # Alta confianza por corrección humana
            }
            
            self.memoria.registrar_patron_nuevo(patron_def, movimiento, validado_humano=True)
            self.estadisticas['patrones_mejorados'] += 1
    
    def mostrar_patrones_similares(self, movimiento: Dict):
        """Muestra patrones similares en la memoria"""
        patrones = self.memoria.buscar_patrones_existentes(movimiento)
        
        if not patrones:
            print(f"\n{Colors.WARNING}No se encontraron patrones similares en memoria{Colors.ENDC}")
            return
        
        print(f"\n{Colors.OKCYAN}PATRONES SIMILARES EN MEMORIA:{Colors.ENDC}")
        for i, patron in enumerate(patrones[:5], 1):
            print(f"\n{i}. Tipo: {patron.get('tipo_patron')}")
            clasificacion = patron.get('clasificacion', {})
            print(f"   Clasificación: {clasificacion.get('tipo')} → {clasificacion.get('categoria')}")
            print(f"   Confianza: {patron.get('confianza', 0)*100:.0f}%")
            print(f"   Frecuencia: {patron.get('frecuencia', 0)} veces")
            if patron.get('validado_humano'):
                print(f"   ✅ Validado por humano")
    
    def mostrar_estadisticas(self):
        """Muestra las estadísticas de la sesión de validación"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}ESTADÍSTICAS DE VALIDACIÓN{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
        
        total = sum([self.estadisticas['confirmaciones'], 
                    self.estadisticas['correcciones'],
                    self.estadisticas['rechazos']])
        
        if total > 0:
            print(f"✅ Confirmaciones: {self.estadisticas['confirmaciones']} ({self.estadisticas['confirmaciones']/total*100:.1f}%)")
            print(f"⚠️  Correcciones: {self.estadisticas['correcciones']} ({self.estadisticas['correcciones']/total*100:.1f}%)")
            print(f"❌ Rechazos: {self.estadisticas['rechazos']} ({self.estadisticas['rechazos']/total*100:.1f}%)")
            print(f"🎯 Patrones mejorados: {self.estadisticas['patrones_mejorados']}")
            
            precision = self.estadisticas['confirmaciones'] / total * 100
            print(f"\n📊 Precisión IA actual: {Colors.BOLD}{precision:.1f}%{Colors.ENDC}")
        else:
            print("No se validaron movimientos")


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validador Humano de Clasificaciones IA')
    parser.add_argument('archivo', help='Archivo JSON con movimientos procesados por IA')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.archivo):
        print(f"{Colors.FAIL}✗ Archivo no encontrado: {args.archivo}{Colors.ENDC}")
        return
    
    validador = ValidadorHumano()
    validador.iniciar_validacion_lote(args.archivo)


if __name__ == "__main__":
    main()