"""
Vista del Wizard de importación BBVA con 6 pasos interactivos
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.http import JsonResponse
from django.db import transaction as db_transaction

from .services.bbva_assistant import AsistenteBBVA
from .models import (
    Cuenta, TipoCuenta, Categoria, ImportacionBBVA, 
    MovimientoBBVATemporal, Transaccion
)


class BBVAWizardView(View):
    """Vista del Wizard interactivo para importación BBVA"""
    template_name = 'bbva/wizard.html'
    
    def get(self, request):
        """Mostrar el paso actual del wizard"""
        paso = int(request.GET.get('paso', 1))
        importacion_id = request.GET.get('importacion_id')
        
        context = {
            'paso_actual': paso,
            'progreso': (paso / 6) * 100
        }
        
        if paso == 1:
            # Paso 1: Selección de archivo
            context['cuentas_bbva'] = Cuenta.objects.filter(
                tipo__grupo='DEB'
            ).filter(referencia__icontains='5019')
            
            if not context['cuentas_bbva'].exists():
                messages.warning(request, 
                    '⚠️ No se encontró cuenta BBVA 5019. Debes crear una cuenta de tipo débito con referencia "5019"')
        
        elif paso == 2 and importacion_id:
            # Paso 2: Análisis del archivo
            importacion = get_object_or_404(ImportacionBBVA, id=importacion_id)
            context['importacion_id'] = importacion_id
            context['info_archivo'] = {
                'fecha_primer_movimiento': importacion.fecha_primer_movimiento,
                'fecha_ultimo_movimiento': importacion.fecha_ultimo_movimiento,
                'total_movimientos': importacion.total_movimientos_archivo,
                'total_cargos': float(importacion.log_proceso.get('total_cargos', 0)),
                'total_abonos': float(importacion.log_proceso.get('total_abonos', 0)),
            }
            # Vista previa de movimientos
            context['movimientos_preview'] = importacion.movimientos_temporales.all()[:5]
        
        elif paso == 3 and importacion_id:
            # Paso 3: Categorías
            importacion = get_object_or_404(ImportacionBBVA, id=importacion_id)
            context['importacion_id'] = importacion_id
            context['movimientos'] = importacion.movimientos_temporales.all()
            context['categorias'] = Categoria.objects.all().order_by('tipo', 'nombre')
        
        elif paso == 4 and importacion_id:
            # Paso 4: Cuentas destino/origen para transferencias
            importacion = get_object_or_404(ImportacionBBVA, id=importacion_id)
            context['importacion_id'] = importacion_id
            context['cuenta_bbva_id'] = importacion.cuenta_bbva.id
            # Solo movimientos de transferencia
            context['movimientos_transferencias'] = importacion.movimientos_temporales.filter(
                tipo_detectado__in=['transferencia_salida', 'transferencia_entrada', 'pago_tdc']
            )
            context['cuentas_todas'] = Cuenta.objects.all().order_by('nombre')
        
        elif paso == 5 and importacion_id:
            # Paso 5: Revisión final
            importacion = get_object_or_404(ImportacionBBVA, id=importacion_id)
            context['importacion_id'] = importacion_id
            
            movimientos = importacion.movimientos_temporales.all()
            context['movimientos_finales'] = movimientos
            context['resumen'] = {
                'total_importar': movimientos.filter(ignorar=False).count(),
                'total_ignorar': movimientos.filter(ignorar=True).count(),
                'cuentas_nuevas': importacion.log_proceso.get('cuentas_nuevas', 0)
            }
        
        elif paso == 6:
            # Paso 6: Resultado
            context['resultado'] = request.session.get('resultado_importacion', {})
        
        return render(request, self.template_name, context)
    
    def post(self, request):
        """Procesar cada paso del wizard"""
        paso = int(request.POST.get('paso', 1))
        action = request.POST.get('action', 'next')
        importacion_id = request.POST.get('importacion_id')
        
        # Navegación hacia atrás
        if action == 'back':
            return redirect(f'/bbva/wizard/?paso={paso-1}&importacion_id={importacion_id}')
        
        if paso == 1:
            # Procesar archivo y crear importación
            archivo = request.FILES.get('archivo_bbva')
            cuenta_id = request.POST.get('cuenta_id')
            
            if not archivo or not cuenta_id:
                messages.error(request, '❌ Debe seleccionar archivo y cuenta')
                return redirect('/bbva/wizard/?paso=1')
            
            try:
                # Paso 1: Leer archivo
                df, info_archivo = AsistenteBBVA.paso1_leer_archivo(archivo)
                
                # Paso 2: Crear importación
                usuario = request.user if request.user.is_authenticated else None
                importacion = AsistenteBBVA.paso2_crear_importacion(
                    archivo, cuenta_id, usuario, info_archivo
                )
                
                # Guardar totales en log
                importacion.log_proceso['total_cargos'] = info_archivo['total_cargos']
                importacion.log_proceso['total_abonos'] = info_archivo['total_abonos']
                importacion.save()
                
                # Paso 3: Analizar movimientos
                AsistenteBBVA.paso3_analizar_movimientos(importacion, df)
                
                messages.success(request, 
                    f"✅ Archivo analizado: {info_archivo['total_movimientos']} movimientos")
                
                return redirect(f'/bbva/wizard/?paso=2&importacion_id={importacion.id}')
                
            except Exception as e:
                messages.error(request, f'❌ Error: {str(e)}')
                return redirect('/bbva/wizard/?paso=1')
        
        elif paso == 2:
            # Continuar al paso 3
            return redirect(f'/bbva/wizard/?paso=3&importacion_id={importacion_id}')
        
        elif paso == 3:
            # Procesar categorías seleccionadas
            importacion = get_object_or_404(ImportacionBBVA, id=importacion_id)
            
            with db_transaction.atomic():
                for mov in importacion.movimientos_temporales.all():
                    # Obtener categoría seleccionada
                    cat_id = request.POST.get(f'categoria_{mov.id}')
                    accion = request.POST.get(f'accion_{mov.id}', 'importar')
                    
                    if cat_id:
                        mov.categoria_confirmada_id = cat_id
                    
                    mov.ignorar = (accion == 'ignorar')
                    mov.validado_por_usuario = True
                    mov.save()
            
            messages.info(request, '✅ Categorías actualizadas')
            return redirect(f'/bbva/wizard/?paso=4&importacion_id={importacion_id}')
        
        elif paso == 4:
            # Procesar cuentas relacionadas
            importacion = get_object_or_404(ImportacionBBVA, id=importacion_id)
            cuentas_nuevas = 0
            
            with db_transaction.atomic():
                for mov in importacion.movimientos_temporales.filter(
                    tipo_detectado__in=['transferencia_salida', 'transferencia_entrada', 'pago_tdc']
                ):
                    cuenta_rel_id = request.POST.get(f'cuenta_rel_{mov.id}')
                    
                    if cuenta_rel_id == 'nueva':
                        # Crear nueva cuenta
                        nombre_nueva = request.POST.get(f'nueva_cuenta_{mov.id}')
                        if nombre_nueva:
                            # Determinar tipo según contexto
                            if 'tarjeta' in nombre_nueva.lower() or 'tdc' in nombre_nueva.lower():
                                tipo = TipoCuenta.objects.filter(codigo='TDC').first()
                            else:
                                tipo = TipoCuenta.objects.filter(codigo='DEB').first()
                            
                            nueva_cuenta = Cuenta.objects.create(
                                nombre=nombre_nueva,
                                referencia=f'EXT-{nombre_nueva[:10].upper()}',
                                moneda='MXN',
                                tipo=tipo,
                                naturaleza='DEUDORA' if tipo.grupo == 'DEB' else 'ACREEDORA'
                            )
                            mov.cuenta_destino_confirmada = nueva_cuenta
                            cuentas_nuevas += 1
                    elif cuenta_rel_id:
                        mov.cuenta_destino_confirmada_id = cuenta_rel_id
                    
                    mov.save()
            
            if cuentas_nuevas > 0:
                importacion.log_proceso['cuentas_nuevas'] = cuentas_nuevas
                importacion.cuentas_creadas = cuentas_nuevas
                importacion.save()
                messages.success(request, f'✅ {cuentas_nuevas} cuenta(s) creada(s)')
            
            return redirect(f'/bbva/wizard/?paso=5&importacion_id={importacion_id}')
        
        elif paso == 5:
            # Confirmar y crear transacciones
            if action == 'confirm':
                importacion = get_object_or_404(ImportacionBBVA, id=importacion_id)
                
                try:
                    # Crear transacciones finales
                    resultado = AsistenteBBVA.paso6_crear_transacciones(importacion)
                    
                    # Guardar resultado en sesión
                    request.session['resultado_importacion'] = resultado
                    
                    if resultado['errores']:
                        messages.warning(request, 
                            f"⚠️ {len(resultado['errores'])} errores durante importación")
                    
                    messages.success(request, 
                        f"✅ {resultado['transacciones_creadas']} transacciones creadas")
                    
                    return redirect('/bbva/wizard/?paso=6')
                    
                except Exception as e:
                    messages.error(request, f'❌ Error: {str(e)}')
                    return redirect(f'/bbva/wizard/?paso=5&importacion_id={importacion_id}')
            
            return redirect(f'/bbva/wizard/?paso=5&importacion_id={importacion_id}')
        
        return redirect('/bbva/wizard/?paso=1')