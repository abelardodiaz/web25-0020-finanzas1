# <!-- file: core/views.py -->
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView
)
from .models import Cuenta, Categoria, TipoCuenta, Periodo
from .forms import CuentaForm, CategoriaForm
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django_filters.views import FilterView
from django.views.generic import CreateView
from .models import Transaccion, TransaccionTipo
from .forms import TransaccionForm, PeriodoForm 
from .filters import TransaccionFilter, CuentaFilter

from django.contrib import messages
from django.db import transaction
from django.db import transaction as db_transaction
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .forms import TransferenciaForm, IngresoForm, forms
from .models import Transaccion, Categoria

import csv, io, pandas as pd

from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Sum
from .forms import EstadoCuentaForm
from .models import Transaccion
from django.http import Http404 
from django import forms as django_forms  
from uuid import uuid4
from decimal import Decimal

# Agregamos importaciones para manejo de fecha de corte base
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
# Nuevo: para filtros compuestos
from django.db.models import Q

# Detalle de periodo / estado de cuenta
from django.views.generic import DetailView
from django.db.models import Sum
from django.db.models import Count

from django.views.generic import View
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from datetime import timedelta
from .models import PeriodoEstadoLog

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from django.http import HttpResponse
from django.http import HttpResponseRedirect

import logging
import re
logger = logging.getLogger(__name__)

from django.shortcuts import render
from django.db.models import Count, Sum
from django.db import connection
from .models import Cuenta, Transaccion, Periodo, Categoria

from django.conf import settings
import os

from django.views.generic.edit import UpdateView
from .models import TipoCuenta, TransaccionEstado
from .forms import TipoCuentaForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
import csv
from datetime import timedelta, datetime
from .models import ImportacionBancaria, MovimientoBancario

class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas de la base de datos
        context['total_cuentas'] = Cuenta.objects.count()
        context['total_transacciones'] = Transaccion.objects.count()
        context['total_periodos'] = Periodo.objects.count()
        context['total_categorias'] = Categoria.objects.count()
        
        # Tamaño de la base de datos (compatible con SQLite)
        try:
            db_path = settings.DATABASES['default']['NAME']
            size_bytes = os.path.getsize(db_path)
            
            # Convertir a formato legible
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024.0:
                    context['db_size'] = f"{size_bytes:.1f} {unit}"
                    break
                size_bytes /= 1024.0
        except Exception as e:
            context['db_size'] = "N/A"
        
        # Cuentas con más movimientos (top 5) - actualizado para v0.6.0
        context['cuentas_movimientos'] = Cuenta.objects.annotate(
            num_movimientos=Count('transacciones_origen') + Count('transacciones_destino')
        ).order_by('-num_movimientos')[:5]
        
        # Últimas transacciones (corregido para v0.6.0)
        context['ultimas_transacciones'] = Transaccion.objects.select_related(
            'categoria', 'cuenta_origen', 'cuenta_destino'  # Campos v0.6.0
        ).order_by('-fecha')[:10]
        
        # Precalcular valores absolutos
        for trans in context['ultimas_transacciones']:
            trans.monto_abs = abs(trans.monto)
        
        # Últimos estados de cuenta con enlace
        context['ultimos_periodos'] = Periodo.objects.select_related('cuenta').order_by('-fecha_fin_periodo')[:5]
        
        # Resumen de saldos por naturaleza (versión corregida)
        saldos_por_naturaleza = {}
        for cuenta in Cuenta.objects.all():
            naturaleza = cuenta.naturaleza if cuenta.naturaleza else "Sin naturaleza"
            saldo_total = cuenta.saldo_inicial + cuenta.saldo()
            
            if naturaleza not in saldos_por_naturaleza:
                saldos_por_naturaleza[naturaleza] = Decimal('0.00')
            saldos_por_naturaleza[naturaleza] += saldo_total
        
        # Convertir a formato para la plantilla
        context['saldos_naturaleza'] = [
            {'naturaleza': key, 'total_saldo': value}
            for key, value in saldos_por_naturaleza.items()
        ]
        
        return context


class CuentasView(TemplateView):
    template_name = "cuentas/index.html"


class CategoriasView(TemplateView):
    template_name = "categorias/index.html"


class TransaccionesView(TemplateView):
    template_name = "transacciones/index.html"


class ReportesView(TemplateView):
    template_name = "reportes/index.html"

# ——— Cuentas ———

class CuentaListView(ListView):
    model = Cuenta
    template_name = 'cuentas/index.html'  # Asegúrate de esta ruta
    context_object_name = 'cuentas'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por búsqueda
        search_query = self.request.GET.get('nombre')
        if search_query:
            queryset = queryset.filter(nombre__icontains=search_query)
        
        # Filtro por tipo de cuenta
        tipo_filter = self.request.GET.get('tipo')
        if tipo_filter:
            queryset = queryset.filter(tipo_id=tipo_filter)

        # Filtro por grupo (usando tipo__grupo)
        grupo_filter = self.request.GET.get('grupo')
        if grupo_filter:
            queryset = queryset.filter(tipo__grupo=grupo_filter)

        # Filtro por estado
        estado_filter = self.request.GET.get('activa')
        if estado_filter:
            queryset = queryset.filter(activa=estado_filter)
        
        return queryset.order_by('nombre')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos_cuenta'] = TipoCuenta.objects.all()
        
        # Obtener grupos disponibles (valores únicos de tipo__grupo)
        context['grupos'] = Cuenta.objects.values_list(
            'tipo__grupo', flat=True
        ).distinct().exclude(tipo__grupo__isnull=True).order_by('tipo__grupo')
        
        context['selected_grupo'] = self.request.GET.get('grupo', '')
        context['selected_tipo'] = self.request.GET.get('tipo', '')
        context['selected_activa'] = self.request.GET.get('activa', '')
        context['search_query'] = self.request.GET.get('nombre', '')
        
        # Obtener y guardar el valor de paginación
        paginate_by = self.request.GET.get('paginate_by', self.paginate_by)
        context['paginate_by'] = int(paginate_by)
        self.paginate_by = paginate_by
        
        return context

class CuentaCreateView(SuccessMessageMixin, CreateView):
    model = Cuenta
    form_class = CuentaForm
    template_name = 'cuentas/cuenta_form.html'
    success_url = reverse_lazy('core:cuentas_list')
    success_message = "Cuenta «%(nombre)s» creada correctamente."

class CuentaUpdateView(SuccessMessageMixin, UpdateView):
    model = Cuenta
    form_class = CuentaForm
    template_name = 'cuentas/cuenta_form.html'
    success_url = reverse_lazy('core:cuentas_list')
    success_message = "Cuenta «%(nombre)s» actualizada correctamente."

class CuentaDeleteView(SuccessMessageMixin, DeleteView):
    model = Cuenta
    template_name = 'cuentas/confirm_delete.html'
    success_url = reverse_lazy('core:cuentas_list')
    success_message = "Cuenta eliminada correctamente."

# ——— Categorías ———

class CategoriaListView(ListView):
    model = Categoria
    template_name = 'categorias/index.html'
    context_object_name = 'categorias'
    paginate_by = 25

class CategoriaCreateView(SuccessMessageMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'categorias/categorias_form.html'
    success_url = reverse_lazy('core:categorias_list')
    success_message = "Categoría «%(nombre)s» creada correctamente."

class CategoriaUpdateView(SuccessMessageMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'categorias/categorias_form.html'
    success_url = reverse_lazy('core:categorias_list')
    success_message = "Categoría «%(nombre)s» actualizada correctamente."

class CategoriaDeleteView(SuccessMessageMixin, DeleteView):
    model = Categoria
    template_name = 'categorias/confirm_delete.html'
    success_url = reverse_lazy('core:categorias_list')
    success_message = "Categoría eliminada correctamente."

# ——— Transacciones ———
class TransaccionListView(FilterView):
    model               = Transaccion
    filterset_class     = TransaccionFilter
    template_name       = "transacciones/index.html"  # Template principal
    context_object_name = "transacciones"
    paginate_by         = 50
    ordering            = ["-fecha"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # v0.6.0: Sin agrupación compleja - cada transacción es independiente
        # Simplemente pasamos las transacciones tal como están
        context['transacciones_v060'] = context['transacciones']
        
        # Para compatibilidad con templates legacy, crear grupos simples
        grupos = []
        for t in context['transacciones']:
            grupos.append({
                'uuid': t.id,  # Usar ID como identificador único
                'transacciones': [t],  # Una transacción por grupo
                'ajuste': False,  # No hay ajustes en v0.6.0
                'transferencia': t.tipo == TransaccionTipo.TRANSFERENCIA
            })
        
        context['grupos'] = grupos
        
        # Agregar estadísticas de estados usando el queryset completo (no paginado)
        queryset_completo = self.get_queryset()
        context['stats_estados'] = {
            'pendientes': queryset_completo.filter(estado=TransaccionEstado.PENDIENTE).count(),
            'liquidadas': queryset_completo.filter(estado=TransaccionEstado.LIQUIDADA).count(), 
            'conciliadas': queryset_completo.filter(estado=TransaccionEstado.CONCILIADA).count(),
            'verificadas': queryset_completo.filter(estado=TransaccionEstado.VERIFICADA).count(),
        }
        
        # Transacciones que requieren atención (solo de la página actual)
        transacciones = context['transacciones']
        context['requieren_atencion'] = [
            t for t in transacciones if t.requiere_atencion
        ]
        
        return context

# === VISTA SIMPLIFICADA v0.6.0 ===
class TransaccionCreateView(SuccessMessageMixin, CreateView):
    model = Transaccion
    form_class = TransaccionForm
    template_name = "transacciones/transacciones_form.html"
    success_url = reverse_lazy("core:transacciones_list")
    success_message = "✅ Transacción registrada exitosamente"

    def form_valid(self, form):
        """Vista simplificada v0.6.0 - sin lógica compleja de doble partida"""
        # El modelo ya maneja la lógica de tipos automáticamente en save()
        return super().form_valid(form)


# ——— Edición de transacciones ———
class TransaccionUpdateView(SuccessMessageMixin, UpdateView):
    model         = Transaccion
    form_class    = TransaccionForm
    template_name = "transacciones/transacciones_form.html"
    success_url   = reverse_lazy("core:transacciones_list")
    success_message = "Transacción actualizada correctamente."

    def form_valid(self, form):
        with transaction.atomic():
            self.object = form.save()

            # Recalcular pareja
            cs = self.object.cuenta_servicio
            mp = self.object.medio_pago
            cond = (not self.object.ajuste) and cs and cs != mp

            pares_qs = Transaccion.objects.filter(grupo_uuid=self.object.grupo_uuid).exclude(pk=self.object.pk)

            if cond:
                # CORRECCIÓN: Usar valor absoluto
                monto_abs = abs(self.object.monto)
                
                if pares_qs.exists():
                    par = pares_qs.first()
                    par.monto = monto_abs  # Usar valor absoluto
                    par.tipo  = (TransaccionTipo.INGRESO if self.object.tipo == TransaccionTipo.GASTO else TransaccionTipo.GASTO)
                    par.fecha = self.object.fecha
                    par.descripcion = f"Pago {self.object.descripcion}"
                    par.cuenta_servicio = cs
                    par.medio_pago = cs
                    par.categoria = self.object.categoria
                    par.moneda = self.object.moneda
                    par.ajuste = False
                    par.save()
                else:
                    Transaccion.objects.create(
                        monto = monto_abs,  # Usar valor absoluto
                        tipo  = (TransaccionTipo.INGRESO if self.object.tipo == TransaccionTipo.GASTO else TransaccionTipo.GASTO),
                        fecha = self.object.fecha,
                        descripcion = f"Pago {self.object.descripcion}",
                        cuenta_servicio = cs,
                        medio_pago = cs,
                        categoria = self.object.categoria,
                        moneda = self.object.moneda,
                        grupo_uuid = self.object.grupo_uuid,
                    )
            else:
                # No debería haber pareja
                pares_qs.delete()

        messages.success(self.request, self.success_message)
        return super().form_valid(form)

class TransaccionDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Transaccion
    template_name = "transacciones/confirm_delete.html"
    success_url = reverse_lazy("core:transacciones_list")
    success_message = "Transacción eliminada correctamente."

class TransferenciaCreateView(FormView):
    template_name  = "transferencias/transferencias_form.html"
    form_class     = TransferenciaForm
    success_url    = reverse_lazy("core:transacciones_list")

    def form_valid(self, form):
        origen   = form.cleaned_data["cuenta_origen"]
        destino  = form.cleaned_data["cuenta_destino"]
        monto    = form.cleaned_data["monto"]
        fecha    = form.cleaned_data["fecha"]
        desc     = form.cleaned_data["descripcion"] or f"Transferencia {origen} → {destino}"

        # Categoría especial "Transferencia interna"
        categoria, _ = Categoria.objects.get_or_create(
            nombre="Transferencia interna", defaults={"tipo": "INTERNA"}
        )

        with transaction.atomic():
            # 1. Abono (sale) en cuenta origen
            t1 = Transaccion.objects.create(
                monto        = -abs(monto),
                tipo         = TransaccionTipo.TRANSFERENCIA,
                fecha        = fecha,
                descripcion  = desc,
                medio_pago   = origen,
                categoria    = categoria,
            )

            # 2. Cargo (entra) en cuenta destino
            t2 = Transaccion.objects.create(
                monto        = abs(monto),
                tipo         = TransaccionTipo.TRANSFERENCIA,
                fecha        = fecha,
                descripcion  = desc,
                medio_pago   = destino,
                categoria    = categoria,
            )

            # 3. Objeto Transferencia que ata ambos movimientos
            Transferencia.objects.create(
                origen       = origen,
                destino      = destino,
                monto        = monto,
                fecha        = fecha,
                descripcion  = desc,
                transaccion_origen  = t1,
                transaccion_destino = t2,
            )

        messages.success(self.request, "Transferencia registrada correctamente.")
        return super().form_valid(form)
    

class EstadoCuentaView(TemplateView):
    template_name = "reportes/estado_cuenta.html"
    paginate_by   = 50   # para movimientos

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        form = EstadoCuentaForm(self.request.GET or None)
        ctx["form"] = form

        if form.is_valid():
            cuenta = form.cleaned_data["cuenta"]
            desde  = form.cleaned_data["desde"]
            hasta  = form.cleaned_data["hasta"]

            # 1) Saldo inicial (antes de 'desde') - v0.6.0
            saldo_inicial = (
                Transaccion.objects
                .filter(Q(cuenta_origen=cuenta) | Q(cuenta_destino=cuenta), fecha__lt=desde)
                .aggregate(total=Sum("monto"))["total"] or 0
            )

            # 2) Movimientos dentro del periodo - v0.6.0
            movs_qs = (
                Transaccion.objects
                .filter(Q(cuenta_origen=cuenta) | Q(cuenta_destino=cuenta), fecha__range=(desde, hasta))
                .select_related("categoria", "cuenta_origen", "cuenta_destino")
                .order_by("-fecha", "-id")
            )

            # Calcular totales correctamente (TODA la consulta, no solo la página)
            total_cargos = sum(abs(m.monto) for m in movs_qs if m.monto < 0)
            total_abonos = sum(m.monto for m in movs_qs if m.monto > 0)

            # Paginación manual (porque usamos TemplateView)
            paginator   = Paginator(movs_qs, self.paginate_by)
            page_number = self.request.GET.get("page")
            page_obj    = paginator.get_page(page_number)

            # Anotar cada transacción en la página actual
            for mov in page_obj:
                mov.es_cargo = mov.monto < 0
                mov.monto_abs = abs(mov.monto)

            # 3) Saldo final
            delta_periodo = movs_qs.aggregate(total=Sum("monto"))["total"] or 0
            saldo_final   = saldo_inicial + delta_periodo

            # 4) Totales por categoría
            tot_cat = (
                movs_qs.values("categoria__nombre")
                .annotate(total=Sum("monto"))
                .order_by("-total")
            )

            # 5) Paginación manual (porque usamos TemplateView)
            paginator   = Paginator(movs_qs, self.paginate_by)
            page_number = self.request.GET.get("page")
            page_obj    = paginator.get_page(page_number)

            # Anotar cada transacción en la página actual
            for mov in page_obj:
                mov.es_cargo = mov.monto < 0
                mov.monto_abs = abs(mov.monto)

            ctx.update({
                "cuenta": cuenta,
                "saldo_inicial": saldo_inicial,
                "saldo_final": saldo_final,
                "total_cargos": total_cargos,
                "total_abonos": total_abonos,
                "delta_periodo": delta_periodo,
                "movs_page": page_obj,
                "totales_categoria": tot_cat,
                "is_paginated": page_obj.has_other_pages(),
            })

            # ----- exportación -----
            export = self.request.GET.get("export")
            if export == "csv":
                return self._export_csv(cuenta, desde, hasta, movs_qs, saldo_inicial, saldo_final)
            if export == "excel":
                return self._export_excel(cuenta, desde, hasta, movs_qs, saldo_inicial, saldo_final)

        return ctx

    # ---------- helpers ----------
    def _export_csv(self, cuenta, desde, hasta, movs, saldo_ini, saldo_fin):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename=estado_{cuenta.id}_{desde}_{hasta}.csv'
        writer = csv.writer(response)
        writer.writerow(["Cuenta", cuenta.nombre])
        writer.writerow(["Desde", desde, "Hasta", hasta])
        writer.writerow([])
        writer.writerow(["Fecha", "Descripción", "Categoría", "Monto"])
        for m in movs.order_by("fecha"):
            writer.writerow([m.fecha, m.descripcion, m.categoria, m.monto])
        writer.writerow([])
        writer.writerow(["Saldo inicial", saldo_ini])
        writer.writerow(["Saldo final", saldo_fin])
        return response

    def _export_excel(self, cuenta, desde, hasta, movs, saldo_ini, saldo_fin):
        # Requiere pandas & openpyxl
        data = [{
            "Fecha": m.fecha,
            "Descripción": m.descripcion,
            "Categoría": m.categoria.nombre if m.categoria else "",
            "Monto": m.monto,
        } for m in movs.order_by("fecha")]
        df = pd.DataFrame(data)
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Movimientos")
            resumen = pd.DataFrame({
                "Concepto": ["Saldo inicial", "Saldo final"],
                "Valor":    [saldo_ini, saldo_fin],
            })
            resumen.to_excel(writer, index=False, sheet_name="Resumen")
        buf.seek(0)
        response = HttpResponse(buf.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = f'attachment; filename=estado_{cuenta.id}_{desde}_{hasta}.xlsx'
        return response


class PeriodoCreateView(CreateView):
    template_name = "periodos/periodos_form.html"
    form_class = PeriodoForm
    success_url = reverse_lazy("core:periodos_list")
    success_message = "Periodo registrado correctamente."

    def dispatch(self, request, *args, **kwargs):
        if "cuenta_pk" in kwargs:
            try:
                self.cuenta = Cuenta.objects.get(pk=kwargs["cuenta_pk"])
                # Usamos los códigos reales DEB y EFE
                TIPOS_PERMITIDOS = ("TDC", "SERV", "DEB", "EFE")  # → puedes moverlo a settings o constants.py

                if self.cuenta.tipo.codigo not in TIPOS_PERMITIDOS:
                    raise Http404("Tipo de cuenta no válido para periodos")
            except Cuenta.DoesNotExist:
                raise Http404("Cuenta no existe")
        else:
            self.cuenta = None
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        if self.cuenta:
            initial['cuenta'] = self.cuenta
            # Solo forzar tipo si hay cuenta predefinida
            initial['tipo'] = self.cuenta.tipo.codigo

            # === NUEVO: cálculo de fecha_corte predeterminada =============
            base_day = getattr(self.cuenta, "dia_corte", None)
            if base_day:
                # 1) Si existe al menos un periodo previo, usa último +1 mes
                last_period = (
                    Periodo.objects.filter(cuenta=self.cuenta)
                    .order_by("-fecha_corte")
                    .first()
                )
                if last_period and last_period.fecha_corte:
                    next_cut = last_period.fecha_corte + relativedelta(months=1)
                else:
                    # 2) Sin periodos previos → usa próximo mes con mismo día
                    today_ = date.today()
                    # Primer intento: próximo mes misma fecha
                    tentative = date(today_.year, today_.month, min(base_day, 28))
                    # Si ya pasó en este mes, sumamos 1 mes para caer en siguiente mes
                    if today_ >= tentative:
                        tentative = tentative + relativedelta(months=1)
                    next_cut = tentative.replace(day=base_day)

                initial.setdefault("fecha_corte", next_cut)
                # Fin de periodo por defecto = fecha_corte
                initial.setdefault("fecha_fin_periodo", next_cut)
            # ==============================================================
        else:
            # 👇 Dejar tipo como None en lugar de cadena vacía
            initial['tipo'] = None  # Corregido: valor nulo válido
        return initial
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['cuenta'] = self.cuenta

        # --- Garantizar diccionario 'initial' --------------------------
        kwargs.setdefault('initial', {})  # crea initial si no existe
        # ---------------------------------------------------------------

        if self.cuenta:
            kwargs['initial']['grupo'] = self.cuenta.tipo.grupo
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cuenta'] = self.cuenta
        
        # Add accounts with group data for template
        if not self.cuenta:
            cuentas = Cuenta.objects.filter(
                tipo__codigo__in=('TDC','SERV','DEB','EFE')
            )
            context['cuentas'] = cuentas
        return context
    
    def form_valid(self, form):
        # Enlazar con periodo anterior de la misma cuenta
        if form.instance.cuenta:
            ultimo = (
                Periodo.objects.filter(cuenta=form.instance.cuenta)
                .exclude(pk=form.instance.pk)
                .order_by('-fecha_corte')
                .first()
            )
            if ultimo:
                form.instance.periodo_anterior = ultimo

        # Marcar como generado
        form.instance.generado = True
        # Guardar primero para obtener instancia
        response = super().form_valid(form)

        # -----------------------------------------------------------------
        # Enlazar movimientos automáticamente al nuevo periodo
        # -----------------------------------------------------------------
        periodo = self.object  # ya guardado

        # 1) Determinar rango de fechas
        inicio = periodo.fecha_corte
        fin    = periodo.fecha_fin_periodo
        
        # Si no hay fecha_fin_periodo, usar fecha_corte + 30 días
        if not fin and periodo.fecha_corte:
            fin = periodo.fecha_corte + timedelta(days=30)

        # 2) Solo si tenemos al menos fecha de fin determinar, asignamos
        if fin:
            # v0.6.0: Actualizar filtros para nuevos campos
            filtros = Q(cuenta_origen=periodo.cuenta) | Q(cuenta_destino=periodo.cuenta)
            if inicio:
                filtros &= Q(fecha__gte=inicio)
                filtros &= ~Q(fecha__lt=inicio) # Excluir explícitamente fechas < inicio
            filtros &= Q(fecha__lte=fin)

            # Actualizar en bloque solo transacciones sin periodo
            Transaccion.objects.filter(filtros, periodo__isnull=True).update(periodo=periodo)

        return response

    def form_invalid(self, form):
        # Agregar datos de depuración al contexto
        context = self.get_context_data(form=form)
        context['debug_info'] = {
            'post_data': self.request.POST.dict(),
            'cleaned_data': getattr(form, 'cleaned_data', {}),
            'errors': form.errors.get_json_data()
        }
        return self.render_to_response(context)


class PeriodoListView(ListView):
    model = Periodo
    template_name = "periodos/index.html"
    context_object_name = "periodos"
    paginate_by = 50

    def get_queryset(self):
        return super().get_queryset().filter(generado=True)


# ----------------------------------------------------------------------
# Detalle de periodo (estado de cuenta)
# ----------------------------------------------------------------------


class PeriodoDetailView(DetailView):
    model = Periodo
    template_name = 'periodos/detalle.html'  # Usa tu template existente
    context_object_name = 'periodo'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        periodo = self.object
        # v0.6.0: Usar cuenta_origen y cuenta_destino en lugar de medio_pago
        movs = Transaccion.objects.filter(
            Q(cuenta_origen=periodo.cuenta) | Q(cuenta_destino=periodo.cuenta),
            fecha__range=(periodo.fecha_inicio or periodo.fecha_corte, periodo.fecha_fin_periodo or periodo.fecha_corte)
        ).order_by("fecha")
        ctx["movs"] = movs
        ctx["total_cargos"] = periodo.total_cargos
        ctx["total_abonos"] = periodo.total_abonos
        ctx["saldo"] = periodo.saldo
        return ctx

# ------------------------------------------------------------------
# Edición y eliminación de periodos
# ------------------------------------------------------------------


class PeriodoUpdateView(UpdateView):
    """Permite editar un periodo existente reutilizando el mismo formulario."""
    model = Periodo
    form_class = PeriodoForm
    template_name = "periodos/periodos_form.html"
    success_url = reverse_lazy("core:periodos_list")
    success_message = "Periodo actualizado correctamente."

    # Queremos permitir cambiar la cuenta, por eso NO fijamos kwargs['cuenta']
    def get_form_kwargs(self):
        return super().get_form_kwargs()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Para que el template muestre el <select>, eliminamos 'cuenta'
        ctx["cuenta"] = None
        # Lista de cuentas disponibles para el selector
        ctx["cuentas"] = Cuenta.objects.filter(tipo__codigo__in=("TDC","SERV","DEB","EFE"))
        return ctx

    def form_valid(self, form):
        # Mantener el estado generado
        form.instance.generado = True
        
        # Reutilizamos la lógica de asignación de transacciones de CreateView
        response = super().form_valid(form)

        periodo = self.object

        # Recalcular rango y volver a vincular movimientos (útil si cambió rango)
        inicio = periodo.fecha_corte
        fin    = periodo.fecha_fin_periodo
        
        # Obtener fechas válidas
        inicio = periodo.fecha_corte
        fin = periodo.fecha_fin_periodo
        
        # Construir filtro base - v0.6.0
        filtros = Q(cuenta_origen=periodo.cuenta) | Q(cuenta_destino=periodo.cuenta)
        
        # Manejar casos donde inicio o fin son nulos
        if inicio and fin:
            filtros &= Q(fecha__range=(inicio, fin))
        elif inicio:
            filtros &= Q(fecha__gte=inicio)
        elif fin:
            filtros &= Q(fecha__lte=fin)

        # Liberar transacciones previamente ligadas si ya no encajan
        Transaccion.objects.filter(periodo=periodo).exclude(filtros).update(periodo=None)
        # Vincular las que correspondan y aún no lo estén
        Transaccion.objects.filter(filtros, periodo__isnull=True).update(periodo=periodo)

        return response


class PeriodoDeleteView(DeleteView):
    """Confirma y elimina un periodo; las transacciones quedan sin periodo."""
    model = Periodo
    template_name = "periodos/confirm_delete.html"
    success_url = reverse_lazy("core:periodos_list")
    success_message = "Periodo eliminado correctamente."

# Actualizar movimientos manualmente (solo si abierto)
class PeriodoRefreshView(View):
    def post(self, request, pk):
        periodo = get_object_or_404(Periodo, pk=pk)
        if periodo.cerrado:
            messages.warning(request, "El período está cerrado y no puede actualizarse.")
            return redirect('core:periodo_detail', pk=pk)

        # --- opción saldo inicial ---
        usar_prev = request.POST.get("usar_saldo_prev", "1") == "1"
        periodo.usar_saldo_prev = usar_prev
        periodo.save(update_fields=["usar_saldo_prev"])  # guarda sólo el flag

        # Reutilizar lógica de vinculación
        inicio = periodo.fecha_corte
        fin = periodo.fecha_fin_periodo or (periodo.fecha_corte + timedelta(days=30))

        # v0.6.0: Actualizar filtros para nuevos campos
        filtros = Q(cuenta_origen=periodo.cuenta) | Q(cuenta_destino=periodo.cuenta)
        if inicio and fin:
            filtros &= Q(fecha__range=(inicio, fin))

        Transaccion.objects.filter(periodo=periodo).exclude(filtros).update(periodo=None)
        Transaccion.objects.filter(filtros, periodo__isnull=True).update(periodo=periodo)

        # Registrar en historial (opcional) - solo si hay usuario autenticado
        if request.user.is_authenticated:
            PeriodoEstadoLog.objects.create(
                periodo=periodo,
                accion="ACTUALIZAR",
                usuario=request.user,
            )
        else:
            # Crear registro sin usuario para acciones no autenticadas
            PeriodoEstadoLog.objects.create(
                periodo=periodo,
                accion="ACTUALIZAR",
                usuario=None  # Permitir valor nulo
            )

        messages.success(request, "Movimientos actualizados correctamente.")
        return redirect('core:periodo_detail', pk=pk)

class CerrarPeriodoView(LoginRequiredMixin, View):
    def post(self, request, pk):
        periodo = get_object_or_404(Periodo, pk=pk)
        if periodo.cerrado:
            messages.info(request, "El período ya estaba cerrado.")
        else:
            periodo.cerrado = True
            periodo.cerrado_por = request.user
            periodo.fecha_cierre = timezone.now()
            periodo.save()
            PeriodoEstadoLog.objects.create(periodo=periodo, accion="CERRAR", usuario=request.user)
            messages.success(request, "Período cerrado correctamente.")
        return redirect('core:periodo_detail', pk=pk)

class CorregirSaldoInicialView(LoginRequiredMixin, View):
    """Permite editar/corregir manualmente el saldo inicial de un periodo"""
    def post(self, request, pk):
        periodo = get_object_or_404(Periodo, pk=pk)
        nuevo = request.POST.get('nuevo_saldo')
        try:
            periodo.saldo_inicial_manual = Decimal(nuevo)
            periodo.save(update_fields=['saldo_inicial_manual'])
            messages.success(request, 'Saldo inicial actualizado.')
        except Exception:
            messages.error(request, 'Valor inválido para saldo inicial.')
        return redirect('core:periodo_detail', pk=pk)


class AbrirPeriodoView(LoginRequiredMixin, View):
    def post(self, request, pk):
        periodo = get_object_or_404(Periodo, pk=pk)
        if not periodo.cerrado:
            messages.info(request, "El período ya estaba abierto.")
        else:
            periodo.cerrado = False
            periodo.cerrado_por = None
            periodo.fecha_cierre = None
            periodo.save()
            PeriodoEstadoLog.objects.create(periodo=periodo, accion="ABRIR", usuario=request.user)
            messages.success(request, "Período reabierto correctamente.")
        return redirect('core:periodo_detail', pk=pk)


# --- NUEVO -------------------------------------------------------------
class IngresoCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    form_class      = IngresoForm
    template_name   = "transacciones/ingreso_form.html"
    success_url     = reverse_lazy("core:transacciones_list")
    success_message = "Ingreso registrado correctamente."


class TipoCuentaListView(ListView):
    model               = TipoCuenta
    template_name       = "tipocuenta/index.html"
    context_object_name = "tipos"
    ordering            = ["nombre"]

class TipoCuentaCreateView(CreateView):
    model = TipoCuenta
    form_class = TipoCuentaForm  # Asegurar que se usa el formulario completo
    template_name = 'tipocuenta/tipocuenta_form.html'
    success_url = reverse_lazy('core:tipocuenta_list')


class TipoCuentaUpdateView(UpdateView):
    model = TipoCuenta
    form_class = TipoCuentaForm  # Asegurar que se usa el formulario completo
    template_name = 'tipocuenta/tipocuenta_form.html'
    success_url = reverse_lazy('core:tipocuenta_list')


class TipoCuentaDeleteView(DeleteView):
    model = TipoCuenta
    template_name = 'tipocuenta/confirm_delete.html'
    success_url = reverse_lazy('core:tipocuenta_list')
    success_message = "Tipo de cuenta eliminado correctamente."


# --- AJAX Endpoints -------------------------------------------------

def cuentas_servicio_json(request):
    cuentas = Cuenta.objects.filter(tipo__grupo="SER").order_by("nombre")
    data = [
        {
            "id": c.id, 
            "text": str(c),
            "naturaleza": c.naturaleza  # Incluir naturaleza
        } for c in cuentas
    ]
    return JsonResponse(data, safe=False)


def categorias_json(request):
    """Devuelve todas las categorías ordenadas por nombre"""
    categorias = Categoria.objects.order_by("nombre")
    data = [{"id": cat.id, "text": str(cat)} for cat in categorias]
    return JsonResponse(data, safe=False)


def medios_pago_json(request):
    cuentas = Cuenta.objects.medios_pago().order_by("nombre")
    data = [
        {
            "id": c.id, 
            "text": str(c),
            "naturaleza": c.naturaleza  # Incluir naturaleza
        } for c in cuentas
    ]
    return JsonResponse(data, safe=False)


class PeriodoPDFView(LoginRequiredMixin, View):
    def get(self, request, pk):
        periodo = get_object_or_404(Periodo, pk=pk)
        # v0.6.0: Actualizar filtro para nuevos campos
        movs = Transaccion.objects.filter(
            Q(cuenta_origen=periodo.cuenta) | Q(cuenta_destino=periodo.cuenta),
            fecha__range=(periodo.fecha_inicio or periodo.fecha_corte, periodo.fecha_fin_periodo or periodo.fecha_corte)
        ).order_by("fecha")
        
        # Crear respuesta HTTP con PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="estado_cuenta_{periodo.id}.pdf"'
        
        # Crear PDF
        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter
        
        # Encabezado
        p.setFont("Helvetica-Bold", 16)
        p.drawString(1*inch, height-1*inch, f"Estado de Cuenta: {periodo.cuenta.nombre}")
        p.setFont("Helvetica", 12)
        p.drawString(1*inch, height-1.2*inch, f"Periodo: {periodo.fecha_corte} - {periodo.fecha_fin_periodo}")
        if periodo.usar_saldo_prev:
            p.drawString(1*inch, height-1.4*inch, f"Saldo inicial: ${periodo.saldo_inicial:.2f}")
        
        # Encabezados de tabla con formato mejorado
        p.setFont("Helvetica-Bold", 10)
        p.drawString(1*inch, height-1.6*inch, "Fecha")
        p.drawString(2.0*inch, height-1.6*inch, "Descripción")
        p.drawString(5.0*inch, height-1.6*inch, "Cargos")  # Columna para cargos
        p.drawString(6.0*inch, height-1.6*inch, "Abonos")  # Columna para abonos
        
        # Línea divisoria debajo de los encabezados
        p.line(1*inch, height-1.65*inch, 7*inch, height-1.65*inch)
        
        y_position = height - 1.8*inch
        p.setFont("Helvetica", 10)
        
        for mov in movs:
            # Formatear fecha
            fecha_str = mov.fecha.strftime("%d/%m/%Y")
            p.drawString(1*inch, y_position, fecha_str)
            
            # Descripción (limitada a 40 caracteres)
            desc = mov.descripcion[:40] + "..." if len(mov.descripcion) > 40 else mov.descripcion
            p.drawString(2.0*inch, y_position, desc)
            
            # Mostrar cargos y abonos en columnas separadas
            if mov.monto < 0:
                # Cargo (valor absoluto)
                cargo = f"${abs(mov.monto):.2f}"
                p.drawRightString(5.5*inch, y_position, cargo)  # Alineado a la derecha
            else:
                # Abono
                abono = f"${mov.monto:.2f}"
                p.drawRightString(6.5*inch, y_position, abono)  # Alineado a la derecha
            
            y_position -= 0.2*inch
            
            # Nueva página si se acaba el espacio
            if y_position < 1*inch:
                p.showPage()
                y_position = height - 1*inch
                # Redibujar encabezados en nueva página
                p.setFont("Helvetica-Bold", 10)
                p.drawString(1*inch, height-0.2*inch, "Fecha")
                p.drawString(2.0*inch, height-0.2*inch, "Descripción")
                p.drawString(5.0*inch, height-0.2*inch, "Cargos")
                p.drawString(6.0*inch, height-0.2*inch, "Abonos")
                p.line(1*inch, height-0.25*inch, 7*inch, height-0.25*inch)
                p.setFont("Helvetica", 10)
                y_position = height - 0.4*inch
        
        # Totales con formato mejorado
        p.setFont("Helvetica-Bold", 12)
        p.drawString(1*inch, y_position - 0.4*inch, f"Total Cargos: ${abs(periodo.total_cargos):.2f}")
        p.drawString(1*inch, y_position - 0.6*inch, f"Total Abonos: ${periodo.total_abonos:.2f}")
        p.drawString(1*inch, y_position - 0.8*inch, f"Saldo Final: ${periodo.saldo:.2f}")
        
        # Línea divisoria sobre los totales
        p.line(1*inch, y_position - 0.35*inch, 7*inch, y_position - 0.35*inch)
        
        p.showPage()
        p.save()
        return response
    

class CuentaSaldosView(TemplateView):
    template_name = "cuentas/saldos_simple.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener todas las cuentas agrupadas por grupo
        grupos = {}
        for cuenta in Cuenta.objects.all().order_by('tipo__grupo', 'nombre'):
            grupo = cuenta.tipo.grupo if cuenta.tipo else "Sin Grupo"
            if grupo not in grupos:
                grupos[grupo] = []
            grupos[grupo].append(cuenta)
        
        context['grupos'] = grupos
        return context

def cuenta_movimientos(request):
    cuenta_id = request.GET.get('cuenta')
    page = request.GET.get('page', 1)
    
    if not cuenta_id:
        return JsonResponse({
            'table': '<p>No se seleccionó cuenta</p>',
            'pagination': ''
        })
    
    cuenta = get_object_or_404(Cuenta, id=cuenta_id)
    
    # Obtener movimientos relacionados con la cuenta
    # v0.6.0: Usar nuevos campos para movimientos de cuenta
    movimientos = Transaccion.objects.filter(
        Q(cuenta_origen=cuenta) | Q(cuenta_destino=cuenta)
    ).order_by('-fecha')
    
    paginator = Paginator(movimientos, 50)  # 50 por página
    page_obj = paginator.get_page(page)
    
    # Renderizar tabla de movimientos
    table_html = render_to_string('cuentas/_movimientos_table.html', {
        'movimientos': page_obj,
        'cuenta': cuenta
    })
    
    # Renderizar paginación
    pagination_html = render_to_string('cuentas/_pagination.html', {
        'page_obj': page_obj
    })
    
    return JsonResponse({
        'table': table_html,
        'pagination': pagination_html
    })


def cuentas_autocomplete(request):
    grupo = request.GET.get('grupo')
    cuentas = []
    
    if grupo:
        cuentas = Cuenta.objects.filter(tipo__grupo=grupo).order_by('nombre')
    
    data = [{
        'id': c.id,
        'text': f"{c.nombre} ({c.tipo.nombre})",
        'nombre': c.nombre,
        'numero': c.numero,
        'naturaleza': c.naturaleza,
        'grupo': c.tipo.grupo,
        'tipo': c.tipo.nombre,
        'saldo': float(c.saldo_actual) if c.saldo_actual else 0.0
    } for c in cuentas]
    
    return JsonResponse(data, safe=False)


class UserProfileView(TemplateView):
    template_name = 'registration/user_profile.html'


class CuentaDetailView(DetailView):
    model = Cuenta
    template_name = 'cuentas/cuenta_detail.html'
    context_object_name = 'cuenta'
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cuenta = self.get_object()
        
        # Obtener saldo inicial
        saldo_inicial = getattr(cuenta, 'saldo_inicial', 0)
        context['saldo_inicial'] = saldo_inicial
        
        # Obtener movimientos paginados - v0.6.0 
        movimientos_origen = cuenta.transacciones_origen.all()
        movimientos_destino = cuenta.transacciones_destino.all()
        # Combinar ambos querysets y ordenar por fecha
        movimientos = movimientos_origen.union(movimientos_destino).order_by('-fecha')
        paginator = Paginator(movimientos, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Lógica corregida para determinar tipo de movimiento
        for movimiento in page_obj:
            # Para todas las cuentas:
            # - Montos positivos = aumentan el saldo
            # - Montos negativos = disminuyen el saldo
            
            # Determinar si es cargo o abono según naturaleza
            if cuenta.naturaleza == "DEUDORA":
                movimiento.es_cargo = movimiento.monto > 0
            else:  # Acreedora
                movimiento.es_cargo = movimiento.monto < 0
            
            # Calcular saldo parcial
            saldo_inicial += movimiento.monto
            movimiento.saldo_parcial = saldo_inicial
            movimiento.display_monto = abs(movimiento.monto)
            movimiento.display_saldo_parcial = abs(saldo_inicial)
        
        context['movimientos'] = page_obj
        return context


# === VISTAS PARA GESTIÓN DE ESTADOS Y CONCILIACIÓN ======================

@require_POST
@csrf_exempt
def cambiar_estado_transaccion(request, transaccion_id):
    """Vista AJAX para cambiar el estado de una transacción"""
    try:
        transaccion = get_object_or_404(Transaccion, id=transaccion_id)
        data = json.loads(request.body)
        nuevo_estado = data.get('estado')
        referencia_bancaria = data.get('referencia_bancaria', '')
        saldo_posterior = data.get('saldo_posterior')
        
        # Validar estado
        estados_validos = [choice[0] for choice in TransaccionEstado.choices]
        if nuevo_estado not in estados_validos:
            return JsonResponse({
                'success': False, 
                'error': 'Estado no válido'
            }, status=400)
        
        # Aplicar cambio de estado
        estado_anterior = transaccion.estado
        
        if nuevo_estado == TransaccionEstado.LIQUIDADA:
            transaccion.marcar_liquidada(referencia_bancaria, saldo_posterior)
        elif nuevo_estado == TransaccionEstado.CONCILIADA:
            transaccion.marcar_conciliada(usuario=request.user)
        elif nuevo_estado == TransaccionEstado.VERIFICADA:
            transaccion.marcar_verificada(usuario=request.user)
        elif nuevo_estado == TransaccionEstado.PENDIENTE:
            transaccion.revertir_estado()
        
        return JsonResponse({
            'success': True,
            'nuevo_estado': transaccion.get_estado_display(),
            'estado_anterior': estado_anterior,
            'fecha_conciliacion': transaccion.fecha_conciliacion.isoformat() if transaccion.fecha_conciliacion else None
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def conciliacion_view(request):
    """Vista principal para conciliación bancaria"""
    # Obtener transacciones no conciliadas agrupadas por cuenta
    transacciones_no_conciliadas = Transaccion.objects.filter(
        estado__in=[TransaccionEstado.PENDIENTE, TransaccionEstado.LIQUIDADA],
        cuenta_origen__isnull=False
    ).select_related(
        'cuenta_origen', 'categoria'
    ).order_by('cuenta_origen__nombre', '-fecha')
    
    # Agrupar por cuenta
    por_cuenta = {}
    for trans in transacciones_no_conciliadas:
        cuenta_key = trans.cuenta_origen.nombre
        if cuenta_key not in por_cuenta:
            por_cuenta[cuenta_key] = {
                'cuenta': trans.cuenta_origen,
                'transacciones': [],
                'total_pendiente': 0
            }
        por_cuenta[cuenta_key]['transacciones'].append(trans)
        por_cuenta[cuenta_key]['total_pendiente'] += trans.monto
    
    # Estadísticas generales
    stats = {
        'total_pendientes': transacciones_no_conciliadas.filter(
            estado=TransaccionEstado.PENDIENTE
        ).count(),
        'total_liquidadas': transacciones_no_conciliadas.filter(
            estado=TransaccionEstado.LIQUIDADA
        ).count(),
        'requieren_atencion': len([
            t for t in transacciones_no_conciliadas if t.requiere_atencion
        ])
    }
    
    return render(request, 'conciliacion/index.html', {
        'por_cuenta': por_cuenta,
        'stats': stats,
        'estados_choices': TransaccionEstado.choices
    })


def conciliar_masivo(request):
    """Vista para conciliar múltiples transacciones"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            transaccion_ids = data.get('transacciones', [])
            
            conciliadas = 0
            errores = []
            
            for trans_id in transaccion_ids:
                try:
                    transaccion = Transaccion.objects.get(id=trans_id)
                    if transaccion.puede_conciliarse:
                        transaccion.marcar_conciliada(usuario=request.user)
                        conciliadas += 1
                    else:
                        errores.append(f"Transacción {trans_id} no puede conciliarse")
                except Transaccion.DoesNotExist:
                    errores.append(f"Transacción {trans_id} no encontrada")
                except Exception as e:
                    errores.append(f"Error en transacción {trans_id}: {str(e)}")
            
            return JsonResponse({
                'success': True,
                'conciliadas': conciliadas,
                'errores': errores
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


class TransaccionEstadoUpdateView(LoginRequiredMixin, View):
    """Vista para actualizar el estado de una transacción individualmente"""
    
    def post(self, request, pk):
        transaccion = get_object_or_404(Transaccion, pk=pk)
        nuevo_estado = request.POST.get('estado')
        
        try:
            if nuevo_estado == TransaccionEstado.LIQUIDADA:
                referencia = request.POST.get('referencia_bancaria', '')
                saldo = request.POST.get('saldo_posterior')
                transaccion.marcar_liquidada(referencia, saldo)
                messages.success(request, 'Transacción marcada como liquidada')
                
            elif nuevo_estado == TransaccionEstado.CONCILIADA:
                transaccion.marcar_conciliada(usuario=request.user)
                messages.success(request, 'Transacción conciliada exitosamente')
                
            elif nuevo_estado == TransaccionEstado.VERIFICADA:
                transaccion.marcar_verificada(usuario=request.user)
                messages.success(request, 'Transacción verificada')
                
            else:
                messages.error(request, 'Estado no válido')
                
        except Exception as e:
            messages.error(request, f'Error al cambiar estado: {str(e)}')
        
        return redirect('core:transacciones_list')


# === VISTAS PARA MATCHING AUTOMÁTICO E IMPORTACIÓN BANCARIA =============

def importacion_bancaria_view(request):
    """Vista principal para importación de estados de cuenta"""
    if request.method == 'POST':
        return procesar_importacion_bancaria(request)
    
    # Mostrar historial de importaciones
    importaciones = ImportacionBancaria.objects.filter(
        usuario=request.user
    ).select_related('cuenta')[:20]
    
    # Cuentas disponibles para importación
    cuentas_disponibles = Cuenta.objects.filter(
        tipo__grupo__in=['DEB', 'CRE']
    ).order_by('nombre')
    
    return render(request, 'conciliacion/importacion.html', {
        'importaciones': importaciones,
        'cuentas_disponibles': cuentas_disponibles,
    })


def procesar_importacion_bancaria(request):
    """Procesa la importación de archivo bancario CSV"""
    try:
        cuenta_id = request.POST.get('cuenta')
        archivo = request.FILES.get('archivo_csv')
        
        if not cuenta_id or not archivo:
            messages.error(request, 'Debe seleccionar una cuenta y un archivo')
            return redirect('core:importacion_bancaria')
        
        cuenta = get_object_or_404(Cuenta, id=cuenta_id)
        
        # Crear registro de importación
        importacion = ImportacionBancaria.objects.create(
            cuenta=cuenta,
            archivo_nombre=archivo.name,
            periodo_inicio=date.today() - timedelta(days=30),  # Default: último mes
            periodo_fin=date.today(),
            usuario=request.user
        )
        
        # Procesar archivo CSV
        try:
            archivo_text = archivo.read().decode('utf-8')
            reader = csv.DictReader(archivo_text.splitlines())
            
            movimientos_creados = 0
            matches_automaticos = 0
            
            for row in reader:
                # Mapear campos del CSV (ajustar según formato bancario)
                try:
                    fecha_str = row.get('fecha', row.get('Fecha', ''))
                    descripcion = row.get('descripcion', row.get('Descripcion', ''))
                    monto_str = row.get('monto', row.get('Monto', '0'))
                    referencia = row.get('referencia', row.get('Referencia', ''))
                    saldo_str = row.get('saldo', row.get('Saldo', ''))
                    
                    # Convertir fecha (formato: DD/MM/YYYY o YYYY-MM-DD)
                    if '/' in fecha_str:
                        fecha = datetime.strptime(fecha_str, '%d/%m/%Y').date()
                    else:
                        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                    
                    # Convertir montos (manejar formato con comas y signos)
                    monto = Decimal(monto_str.replace(',', '').replace('$', ''))
                    saldo = Decimal(saldo_str.replace(',', '').replace('$', '')) if saldo_str else None
                    
                    # Crear movimiento bancario
                    movimiento = MovimientoBancario.objects.create(
                        importacion=importacion,
                        fecha=fecha,
                        descripcion=descripcion,
                        referencia=referencia,
                        monto=monto,
                        saldo_posterior=saldo
                    )
                    
                    movimientos_creados += 1
                    
                    # Intentar matching automático
                    match_exitoso, mensaje = movimiento.aplicar_match_automatico()
                    if match_exitoso:
                        matches_automaticos += 1
                        
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error procesando fila del CSV: {e}")
                    continue
            
            # Actualizar estadísticas de importación
            importacion.total_registros = movimientos_creados
            importacion.registros_procesados = movimientos_creados
            importacion.registros_conciliados = matches_automaticos
            importacion.save()
            
            messages.success(
                request, 
                f"Importación completada: {movimientos_creados} movimientos, "
                f"{matches_automaticos} conciliaciones automáticas"
            )
            
        except Exception as e:
            importacion.delete()  # Limpiar importación fallida
            messages.error(request, f"Error procesando archivo: {str(e)}")
            return redirect('core:importacion_bancaria')
        
        return redirect('core:importacion_detalle', importacion_id=importacion.id)
        
    except Exception as e:
        messages.error(request, f"Error en importación: {str(e)}")
        return redirect('core:importacion_bancaria')


def importacion_detalle_view(request, importacion_id):
    """Vista de detalle de una importación específica"""
    importacion = get_object_or_404(ImportacionBancaria, id=importacion_id)
    
    # Movimientos de la importación con estado de conciliación
    movimientos = importacion.movimientos.select_related(
        'transaccion_conciliada'
    ).order_by('-fecha')
    
    # Estadísticas
    stats = {
        'total': movimientos.count(),
        'conciliados': movimientos.filter(conciliado=True).count(),
        'pendientes': movimientos.filter(conciliado=False).count(),
        'exactos': movimientos.filter(confianza_match='EXACTA').count(),
        'altos': movimientos.filter(confianza_match='ALTA').count(),
        'medios': movimientos.filter(confianza_match='MEDIA').count(),
    }
    
    return render(request, 'conciliacion/importacion_detalle.html', {
        'importacion': importacion,
        'movimientos': movimientos,
        'stats': stats,
    })


@require_POST
def aplicar_match_manual(request):
    """Aplica match manual entre movimiento bancario y transacción"""
    try:
        data = json.loads(request.body)
        movimiento_id = data.get('movimiento_id')
        transaccion_id = data.get('transaccion_id')
        
        movimiento = get_object_or_404(MovimientoBancario, id=movimiento_id)
        transaccion = get_object_or_404(Transaccion, id=transaccion_id)
        
        # Validar que la transacción pueda conciliarse
        if not transaccion.puede_conciliarse:
            return JsonResponse({
                'success': False,
                'error': 'La transacción no puede conciliarse en su estado actual'
            })
        
        # Aplicar match manual
        with transaction.atomic():
            # Marcar transacción como liquidada
            transaccion.marcar_liquidada(
                referencia_bancaria=movimiento.referencia,
                saldo_posterior=movimiento.saldo_posterior
            )
            
            # Vincular movimiento con transacción
            movimiento.transaccion_conciliada = transaccion
            movimiento.confianza_match = 'MANUAL'
            movimiento.conciliado = True
            movimiento.fecha_conciliacion = timezone.now()
            movimiento.save()
            
            # Actualizar estadísticas de importación
            importacion = movimiento.importacion
            importacion.registros_conciliados = importacion.movimientos.filter(
                conciliado=True
            ).count()
            importacion.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Match manual aplicado exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_POST
def revertir_match(request):
    """Revierte un match entre movimiento bancario y transacción"""
    try:
        data = json.loads(request.body)
        movimiento_id = data.get('movimiento_id')
        
        movimiento = get_object_or_404(MovimientoBancario, id=movimiento_id)
        
        if not movimiento.conciliado:
            return JsonResponse({
                'success': False,
                'error': 'El movimiento no está conciliado'
            })
        
        with transaction.atomic():
            # Revertir estado de transacción
            if movimiento.transaccion_conciliada:
                movimiento.transaccion_conciliada.revertir_estado()
            
            # Limpiar match
            movimiento.transaccion_conciliada = None
            movimiento.confianza_match = 'MANUAL'
            movimiento.conciliado = False
            movimiento.fecha_conciliacion = None
            movimiento.save()
            
            # Actualizar estadísticas
            importacion = movimiento.importacion
            importacion.registros_conciliados = importacion.movimientos.filter(
                conciliado=True
            ).count()
            importacion.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Match revertido exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def buscar_transacciones_candidatas(request):
    """API para buscar transacciones candidatas para matching manual"""
    movimiento_id = request.GET.get('movimiento_id')
    
    if not movimiento_id:
        return JsonResponse({'error': 'ID de movimiento requerido'}, status=400)
    
    movimiento = get_object_or_404(MovimientoBancario, id=movimiento_id)
    candidatos = movimiento.buscar_coincidencias()
    
    # Formatear para JSON
    data = []
    for candidato in candidatos:
        transaccion = candidato['transaccion']
        data.append({
            'id': transaccion.id,
            'fecha': transaccion.fecha.isoformat(),
            'descripcion': transaccion.descripcion,
            'monto': str(transaccion.monto),
            'categoria': transaccion.categoria.nombre if transaccion.categoria else '',
            'estado': transaccion.get_estado_display(),
            'confianza': candidato['confianza'],
            'score': candidato['score'],
            'criterios': candidato['criterios']
        })
    
    return JsonResponse({'candidatos': data})


def ejecutar_matching_masivo(request, importacion_id):
    """Ejecuta matching automático para toda una importación"""
    importacion = get_object_or_404(ImportacionBancaria, id=importacion_id)
    
    movimientos_pendientes = importacion.movimientos.filter(conciliado=False)
    
    matches_exitosos = 0
    total_procesados = 0
    
    for movimiento in movimientos_pendientes:
        total_procesados += 1
        match_exitoso, mensaje = movimiento.aplicar_match_automatico()
        if match_exitoso:
            matches_exitosos += 1
    
    # Actualizar estadísticas
    importacion.registros_conciliados = importacion.movimientos.filter(
        conciliado=True
    ).count()
    importacion.save()
    
    messages.success(
        request,
        f"Matching masivo completado: {matches_exitosos} de {total_procesados} movimientos conciliados"
    )
    
    return redirect('core:importacion_detalle', importacion_id=importacion.id)


# ============================================================================
# VISTAS BBVA - Sistema de importación asistida
# ============================================================================

from .services.bbva_assistant import AsistenteBBVA
from .models import ImportacionBBVA, MovimientoBBVATemporal
from .bbva_wizard_view import BBVAWizardView


class BBVASimpleView(View):
    """Vista simple para probar importación BBVA"""
    template_name = 'bbva/simple.html'
    
    def get(self, request):
        """Mostrar formulario de importación"""
        # Buscar cuentas BBVA (tipo débito que contenga 5019 en referencia)
        cuentas_bbva = Cuenta.objects.filter(
            tipo__grupo='DEB'
        ).filter(referencia__icontains='5019')
        
        # Si no hay cuentas BBVA, sugerir crear una
        if not cuentas_bbva.exists():
            messages.warning(request, 
                '⚠️ No se encontró cuenta BBVA 5019. Debes crear una cuenta de tipo débito con referencia que contenga "5019"')
        
        # Importaciones recientes (todas si no hay usuario)
        if request.user.is_authenticated:
            importaciones_recientes = ImportacionBBVA.objects.filter(
                usuario=request.user
            )[:10]
        else:
            importaciones_recientes = ImportacionBBVA.objects.all()[:10]
        
        return render(request, self.template_name, {
            'cuentas_bbva': cuentas_bbva,
            'importaciones_recientes': importaciones_recientes
        })
    
    def post(self, request):
        """Procesar archivo BBVA"""
        archivo = request.FILES.get('archivo_bbva')
        cuenta_id = request.POST.get('cuenta_id')
        
        if not archivo:
            messages.error(request, '❌ Debe seleccionar un archivo')
            return redirect('core:bbva_simple')
        
        if not cuenta_id:
            messages.error(request, '❌ Debe seleccionar una cuenta BBVA')
            return redirect('core:bbva_simple')
        
        try:
            # Paso 1: Leer archivo
            df, info_archivo = AsistenteBBVA.paso1_leer_archivo(archivo)
            
            messages.success(request, 
                f"✅ Archivo leído: {info_archivo['total_movimientos']} movimientos detectados")
            messages.info(request, 
                f"📅 Periodo: {info_archivo['fecha_primer_movimiento']} - {info_archivo['fecha_ultimo_movimiento']}")
            messages.info(request, 
                f"💰 Cargos: ${info_archivo['total_cargos']:.2f}, Abonos: ${info_archivo['total_abonos']:.2f}")
            
            # Paso 2: Crear importación (usar usuario o None)
            usuario = request.user if request.user.is_authenticated else None
            importacion = AsistenteBBVA.paso2_crear_importacion(
                archivo, cuenta_id, usuario, info_archivo
            )
            
            # Paso 3: Analizar movimientos
            movimientos_temporales = AsistenteBBVA.paso3_analizar_movimientos(importacion, df)
            
            messages.success(request, 
                f"✅ Análisis completado: {len(movimientos_temporales)} movimientos analizados")
            
            # Redirigir al wizard detallado para revisar movimiento por movimiento
            messages.info(request, 
                f"🔍 Ahora revisaremos cada uno de los {len(movimientos_temporales)} movimientos paso a paso")
            return redirect('core:bbva_wizard_detallado', importacion_id=importacion.id)
            
        except Exception as e:
            messages.error(request, f'❌ Error procesando archivo: {str(e)}')
            return redirect('core:bbva_simple')


class BBVADetalleView(View):
    """Vista detalle de una importación"""
    template_name = 'bbva/detalle.html'
    
    def get(self, request, importacion_id):
        """Mostrar detalle de importación"""
        # Obtener importación (filtrar por usuario solo si está autenticado)
        if request.user.is_authenticated:
            importacion = get_object_or_404(
                ImportacionBBVA, 
                id=importacion_id, 
                usuario=request.user
            )
        else:
            importacion = get_object_or_404(ImportacionBBVA, id=importacion_id)
        
        # Obtener movimientos paginados
        page = int(request.GET.get('page', 1))
        per_page = 20
        
        movimientos = importacion.movimientos_temporales.all()
        start = (page - 1) * per_page
        end = start + per_page
        movimientos_pagina = movimientos[start:end]
        
        # Calcular paginación
        total_pages = (movimientos.count() + per_page - 1) // per_page
        
        # Obtener resumen
        resumen = AsistenteBBVA.obtener_resumen_importacion(importacion)
        
        return render(request, self.template_name, {
            'importacion': importacion,
            'movimientos': movimientos_pagina,
            'resumen': resumen,
            'page': page,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        })
    
    def post(self, request, importacion_id):
        """Procesar confirmaciones y crear transacciones"""
        # Obtener importación (filtrar por usuario solo si está autenticado)
        if request.user.is_authenticated:
            importacion = get_object_or_404(
                ImportacionBBVA,
                id=importacion_id,
                usuario=request.user
            )
        else:
            importacion = get_object_or_404(ImportacionBBVA, id=importacion_id)
        
        try:
            # Marcar todos los movimientos como validados (versión simple)
            importacion.movimientos_temporales.update(
                validado_por_usuario=True,
                ignorar=False
            )
            
            # Crear transacciones
            resultado = AsistenteBBVA.paso6_crear_transacciones(importacion)
            
            if resultado['errores']:
                messages.warning(request, 
                    f"⚠️ {len(resultado['errores'])} errores durante importación")
                for error in resultado['errores'][:5]:  # Mostrar solo los primeros 5
                    messages.error(request, error)
            
            messages.success(request, 
                f"✅ Importación completada: {resultado['transacciones_creadas']} transacciones creadas")
            
            return redirect('core:transacciones_list')
            
        except Exception as e:
            messages.error(request, f'❌ Error creando transacciones: {str(e)}')
            return redirect('core:bbva_detalle', importacion_id=importacion.id)


def bbva_validar_movimiento(request, movimiento_id):
    """AJAX para validar un movimiento individual"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        # Filtrar por usuario solo si está autenticado
        if request.user.is_authenticated:
            movimiento = get_object_or_404(
                MovimientoBBVATemporal,
                id=movimiento_id,
                importacion__usuario=request.user
            )
        else:
            movimiento = get_object_or_404(MovimientoBBVATemporal, id=movimiento_id)
        
        # Actualizar movimiento
        movimiento.descripcion_limpia = request.POST.get('descripcion', movimiento.descripcion_limpia)
        movimiento.ignorar = request.POST.get('ignorar') == 'true'
        movimiento.notas_usuario = request.POST.get('notas', '')
        movimiento.validado_por_usuario = True
        movimiento.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Movimiento actualizado'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)


def bbva_resumen_importacion(request, importacion_id):
    """AJAX para obtener resumen actualizado"""
    try:
        # Filtrar por usuario solo si está autenticado
        if request.user.is_authenticated:
            importacion = get_object_or_404(
                ImportacionBBVA,
                id=importacion_id,
                usuario=request.user
            )
        else:
            importacion = get_object_or_404(ImportacionBBVA, id=importacion_id)
        
        resumen = AsistenteBBVA.obtener_resumen_importacion(importacion)
        
        return JsonResponse({
            'success': True,
            'resumen': resumen
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)




# ============================================================================
# WIZARD BBVA DETALLADO - Movimiento por movimiento
# ============================================================================


class BBVAWizardDetalladoView(View):
    """Wizard detallado que revisa cada movimiento individualmente"""
    template_name = 'bbva/wizard_movimiento.html'
    
    def get(self, request, importacion_id):
        """Mostrar el movimiento actual para revisión"""
        importacion = get_object_or_404(ImportacionBBVA, id=importacion_id)
        
        # Obtener número de movimiento actual (por defecto 1)
        movimiento_num = int(request.GET.get('mov', 1))
        
        # Obtener todos los movimientos ordenados
        movimientos = importacion.movimientos_temporales.all().order_by('fila_excel')
        total_movimientos = movimientos.count()
        
        if movimiento_num > total_movimientos:
            # Si ya revisamos todos, mostrar resumen
            return redirect('core:bbva_resumen_final', importacion_id=importacion_id)
        
        # Obtener el movimiento actual
        movimiento = movimientos[movimiento_num - 1]
        
        # Detectar información de la cuenta relacionada
        info_detectada = self.detectar_info_cuenta(movimiento)
        
        # Buscar si ya existe una cuenta similar
        cuenta_sugerida = self.buscar_cuenta_existente(info_detectada)
        
        context = {
            'importacion': importacion,
            'movimiento': movimiento,
            'movimiento_actual': movimiento_num,
            'total_movimientos': total_movimientos,
            'progreso': (movimiento_num / total_movimientos) * 100,
            'movimientos_indices': list(range(1, min(total_movimientos + 1, 13))),  # Max 12 indicadores
            'cuenta_bbva': importacion.cuenta_bbva,
            'categorias': Categoria.objects.all().order_by('tipo', 'nombre'),
            'cuentas_existentes': Cuenta.objects.all().order_by('nombre'),
            'tipos_cuenta': TipoCuenta.objects.all().order_by('nombre'),
            'cuenta_sugerida': cuenta_sugerida,
            'banco_detectado': info_detectada.get('banco'),
            'numero_detectado': info_detectada.get('numero'),
            'nombre_cuenta_sugerido': info_detectada.get('nombre_cuenta'),
            'referencia_sugerida': info_detectada.get('referencia'),
            'tipo_sugerido': info_detectada.get('tipo_cuenta'),
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request, importacion_id):
        """Procesar la confirmación del movimiento actual"""
        importacion = get_object_or_404(ImportacionBBVA, id=importacion_id)
        
        movimiento_id = request.POST.get('movimiento_id')
        movimiento = get_object_or_404(MovimientoBBVATemporal, id=movimiento_id)
        
        accion = request.POST.get('accion', 'siguiente')
        
        # Obtener número de movimiento actual
        movimientos = importacion.movimientos_temporales.all().order_by('fila_excel')
        movimiento_num = list(movimientos).index(movimiento) + 1
        
        if accion == 'anterior':
            # Ir al movimiento anterior
            if movimiento_num > 1:
                return redirect(f'/bbva/wizard-detallado/{importacion_id}/?mov={movimiento_num - 1}')
        
        elif accion == 'resumen':
            # Guardar cambios y mostrar resumen
            self.guardar_movimiento(request, movimiento)
            return redirect('core:bbva_resumen_final', importacion_id=importacion_id)
        
        else:  # siguiente
            # Guardar los cambios del movimiento actual
            self.guardar_movimiento(request, movimiento)
            
            # Ir al siguiente movimiento
            if movimiento_num < movimientos.count():
                messages.success(request, f'✅ Movimiento {movimiento_num} guardado')
                return redirect(f'/bbva/wizard-detallado/{importacion_id}/?mov={movimiento_num + 1}')
            else:
                # Era el último, ir al resumen
                return redirect('core:bbva_resumen_final', importacion_id=importacion_id)
        
        return redirect(f'/bbva/wizard-detallado/{importacion_id}/?mov={movimiento_num}')
    
    def guardar_movimiento(self, request, movimiento):
        """Guardar los cambios del movimiento"""
        with db_transaction.atomic():
            # Actualizar descripción
            movimiento.descripcion_limpia = request.POST.get('descripcion', movimiento.descripcion_limpia)
            
            # Actualizar categoría
            categoria_id = request.POST.get('categoria_id')
            if categoria_id:
                movimiento.categoria_confirmada_id = categoria_id
            
            # Marcar para ignorar si aplica
            movimiento.ignorar = request.POST.get('ignorar') == 'true'
            
            # Manejar cuenta relacionada
            cuenta_rel_id = request.POST.get('cuenta_relacionada_id')
            
            if cuenta_rel_id == 'nueva':
                # Crear nueva cuenta
                nombre = request.POST.get('nueva_cuenta_nombre')
                referencia = request.POST.get('nueva_cuenta_referencia')
                tipo_id = request.POST.get('nueva_cuenta_tipo')
                
                if nombre and tipo_id:
                    tipo = TipoCuenta.objects.get(id=tipo_id)
                    nueva_cuenta = Cuenta.objects.create(
                        nombre=nombre,
                        referencia=referencia or f'AUTO-{movimiento.id}',
                        moneda='MXN',
                        tipo=tipo,
                        naturaleza='DEUDORA' if tipo.grupo in ['DEB', 'EFE'] else 'ACREEDORA',
                        saldo_inicial=0,
                        activa=True,
                        descripcion=f'Creada desde importación BBVA'
                    )
                    movimiento.cuenta_destino_confirmada = nueva_cuenta
            elif cuenta_rel_id:
                # Usar cuenta existente
                movimiento.cuenta_destino_confirmada_id = cuenta_rel_id
            
            # Marcar como validado por usuario
            movimiento.validado_por_usuario = True
            movimiento.save()
    
    def detectar_info_cuenta(self, movimiento):
        """Detectar información de la cuenta desde la descripción"""
        descripcion = movimiento.descripcion_original.upper()
        info = {}
        
        # Patrones de bancos
        patrones_banco = {
            'SANTANDER': 'Santander',
            'BANORTE': 'Banorte',
            'BANAMEX': 'Banamex',
            'BANCOMER': 'Bancomer',
            'BBVA': 'BBVA',
            'HSBC': 'HSBC',
            'SCOTIABANK': 'Scotiabank',
            'INBURSA': 'Inbursa',
            'AZTECA': 'Banco Azteca',
            'STP': 'STP',
            'MERCADO PAGO': 'Mercado Pago',
            'NU MEXICO': 'Nu Bank',
            'CONSUBANCO': 'Consubanco'
        }
        
        # Detectar banco
        for patron, nombre in patrones_banco.items():
            if patron in descripcion:
                info['banco'] = nombre
                break
        
        # Detectar número de cuenta
        match = re.search(r'(\d{10,})', descripcion)
        if match:
            info['numero'] = match.group(1)[:10]
            info['referencia'] = match.group(1)[:10]
        
        # Sugerir nombre de cuenta
        if 'banco' in info:
            if 'ENVIADO' in descripcion:
                info['nombre_cuenta'] = f"{info['banco']} - Destino"
            else:
                info['nombre_cuenta'] = f"{info['banco']} - Origen"
        elif 'PAGO CUENTA DE TERCERO' in descripcion:
            info['nombre_cuenta'] = "Depósito de Tercero"
            info['banco'] = "Externo"
        else:
            info['nombre_cuenta'] = "Cuenta Externa"
        
        # Sugerir tipo de cuenta
        if 'TARJETA' in descripcion or 'TDC' in descripcion:
            info['tipo_cuenta'] = TipoCuenta.objects.filter(codigo='TDC').first()
        elif 'MERCADO PAGO' in descripcion:
            info['tipo_cuenta'] = TipoCuenta.objects.filter(codigo='DIG').first()
        else:
            info['tipo_cuenta'] = TipoCuenta.objects.filter(codigo='DEB').first()
        
        return info
    
    def buscar_cuenta_existente(self, info_detectada):
        """Buscar si ya existe una cuenta con características similares"""
        if not info_detectada:
            return None
        
        # Buscar por número/referencia
        if 'numero' in info_detectada:
            cuenta = Cuenta.objects.filter(
                referencia__contains=info_detectada['numero']
            ).first()
            if cuenta:
                return cuenta
        
        # Buscar por nombre del banco
        if 'banco' in info_detectada:
            cuenta = Cuenta.objects.filter(
                nombre__icontains=info_detectada['banco']
            ).first()
            if cuenta:
                return cuenta
        
        return None


class BBVAResumenFinalView(View):
    """Vista del resumen final antes de crear las transacciones"""
    template_name = 'bbva/resumen_final.html'
    
    def get(self, request, importacion_id):
        """Mostrar resumen de todos los movimientos configurados"""
        importacion = get_object_or_404(ImportacionBBVA, id=importacion_id)
        
        movimientos = importacion.movimientos_temporales.filter(
            validado_por_usuario=True
        ).order_by('fila_excel')
        
        # Contar estadísticas
        stats = {
            'total_validados': movimientos.count(),
            'total_ignorados': movimientos.filter(ignorar=True).count(),
            'total_importar': movimientos.filter(ignorar=False).count(),
            'cuentas_nuevas': set(),  # Cuentas que se crearán
            'total_gastos': 0,
            'total_ingresos': 0,
        }
        
        # Calcular totales y cuentas nuevas
        for mov in movimientos.filter(ignorar=False):
            if mov.es_gasto:
                stats['total_gastos'] += float(mov.monto_calculado)
            else:
                stats['total_ingresos'] += float(mov.monto_calculado)
            
            # Ver si la cuenta es nueva (no tiene ID)
            if mov.cuenta_destino_confirmada and not mov.cuenta_destino_confirmada.pk:
                stats['cuentas_nuevas'].add(mov.cuenta_destino_confirmada.nombre)
        
        stats['total_cuentas_nuevas'] = len(stats['cuentas_nuevas'])
        
        context = {
            'importacion': importacion,
            'movimientos': movimientos,
            'stats': stats,
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request, importacion_id):
        """Confirmar y crear todas las transacciones"""
        importacion = get_object_or_404(ImportacionBBVA, id=importacion_id)
        
        try:
            # Crear transacciones finales
            resultado = AsistenteBBVA.paso6_crear_transacciones(importacion)
            
            if resultado['errores']:
                messages.warning(request, 
                    f"⚠️ {len(resultado['errores'])} errores durante importación")
                for error in resultado['errores'][:3]:
                    messages.error(request, error)
            
            messages.success(request, 
                f"✅ Importación completada: {resultado['transacciones_creadas']} transacciones creadas")
            
            # Limpiar sesión
            if 'importacion_bbva_id' in request.session:
                del request.session['importacion_bbva_id']
            
            return redirect('core:transacciones_list')
            
        except Exception as e:
            messages.error(request, f'❌ Error creando transacciones: {str(e)}')
            return redirect('core:bbva_resumen_final', importacion_id=importacion_id)