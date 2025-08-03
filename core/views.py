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
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .forms import TransferenciaForm, IngresoForm, forms
from .models import Transaccion, Transferencia, Categoria

import csv, io, pandas as pd

from django.views.generic import TemplateView
from django.http import HttpResponse
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
logger = logging.getLogger(__name__)

from django.shortcuts import render
from django.db.models import Count, Sum
from django.db import connection
from .models import Cuenta, Transaccion, Periodo, Categoria

from django.conf import settings
import os

from django.views.generic.edit import UpdateView
from .models import TipoCuenta

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
        
        # Cuentas con más movimientos (top 5)
        context['cuentas_movimientos'] = Cuenta.objects.annotate(
            num_movimientos=Count('transacciones_pago')
        ).order_by('-num_movimientos')[:5]
        
        # Últimas transacciones (corregido)
        context['ultimas_transacciones'] = Transaccion.objects.select_related(
            'categoria', 'medio_pago'  # Campos válidos
        ).order_by('-fecha')[:10]
        
        # Precalcular valores absolutos
        for trans in context['ultimas_transacciones']:
            trans.monto_abs = abs(trans.monto)
        
        # Últimos estados de cuenta con enlace
        context['ultimos_periodos'] = Periodo.objects.select_related('cuenta').order_by('-fecha_fin_periodo')[:5]
        
        # Resumen de saldos por naturaleza (versión corregida)
        saldos_por_naturaleza = {}
        for cuenta in Cuenta.objects.all():
            naturaleza = cuenta.tipo.naturaleza if cuenta.tipo else "Sin naturaleza"
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
    template_name = 'cuentas/cuentas_form.html'
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
    template_name       = "transacciones/index.html"
    context_object_name = "transacciones"
    paginate_by         = 50
    ordering            = ["-fecha"]  # redundante: ya viene del Meta

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Agrupar transacciones por grupo_uuid
        grupos = {}
        for t in context['transacciones']:
            grupo = grupos.setdefault(t.grupo_uuid, {
                'uuid': t.grupo_uuid,
                'transacciones': [],
                'ajuste': t.ajuste,
                'transferencia': t.tipo == TransaccionTipo.TRANSFERENCIA
            })
            grupo['transacciones'].append(t)
        
        context['grupos'] = grupos.values()
        return context

class TransaccionCreateView(SuccessMessageMixin, CreateView):
    model         = Transaccion
    form_class    = TransaccionForm
    template_name = "transacciones/transacciones_form.html"
    success_url   = reverse_lazy("core:transacciones_list")
    success_message = "Transacción registrada exitosamente."

    def form_valid(self, form):
        with transaction.atomic():
            tipo = form.cleaned_data["tipo"]
            if tipo == TransaccionTipo.TRANSFERENCIA:
                origen   = form.cleaned_data["medio_pago"]
                destino  = form.cleaned_data["cuenta_servicio"]
                monto    = abs(form.cleaned_data["monto"])
                fecha    = form.cleaned_data["fecha"]
                desc     = form.cleaned_data["descripcion"] or f"Transferencia {origen} → {destino}"

                # Categoría especial
                categoria, _ = Categoria.objects.get_or_create(nombre="Transferencia interna", defaults={"tipo": "INTERNA"})

                grupo = uuid4()
                t1 = Transaccion.objects.create(
                    monto=-monto,
                    tipo=TransaccionTipo.GASTO,
                    fecha=fecha,
                    descripcion=desc,
                    medio_pago=origen,
                    categoria=categoria,
                    grupo_uuid=grupo,
                )
                t2 = Transaccion.objects.create(
                    monto=monto,
                    tipo=TransaccionTipo.INGRESO,
                    fecha=fecha,
                    descripcion=desc,
                    medio_pago=destino,
                    categoria=categoria,
                    grupo_uuid=grupo,
                )
                # Establecer self.object para evitar el error
                self.object = t1
                messages.success(self.request, "Transferencia registrada correctamente.")
                return HttpResponseRedirect(self.get_success_url())  # Cambiado

            # 1) movimiento principal estándar
            self.object = form.save()

            # 2) ¿hay doble partida para servicio?
            cs  = self.object.cuenta_servicio
            mp  = self.object.medio_pago
            if (not self.object.ajuste) and cs and cs != mp:
                # CORRECCIÓN: Usar el valor absoluto del monto
                monto_abs = abs(self.object.monto)
                
                Transaccion.objects.create(
                    monto        = monto_abs,  # Usar valor absoluto
                    tipo         = (TransaccionTipo.INGRESO
                                        if self.object.tipo == TransaccionTipo.GASTO
                                        else TransaccionTipo.GASTO),
                    fecha        = self.object.fecha,
                    descripcion  = f"Pago {self.object.descripcion}",
                    cuenta_servicio = cs,
                    medio_pago      = cs,
                    categoria    = self.object.categoria,
                    moneda       = self.object.moneda,
                    grupo_uuid   = self.object.grupo_uuid,
                )
        messages.success(self.request, self.success_message)
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

            # 1) Saldo inicial (antes de 'desde')
            saldo_inicial = (
                Transaccion.objects
                .filter(medio_pago=cuenta, fecha__lt=desde)
                .aggregate(total=Sum("monto"))["total"] or 0
            )

            # 2) Movimientos dentro del periodo
            movs_qs = (
                Transaccion.objects
                .filter(medio_pago=cuenta, fecha__range=(desde, hasta))
                .select_related("categoria")
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

            ctx.update({
                "cuenta": cuenta,
                "saldo_inicial": saldo_inicial,
                "saldo_final": saldo_final,
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
            filtros = Q(medio_pago=periodo.cuenta) | Q(cuenta_servicio=periodo.cuenta)
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
        movs = Transaccion.objects.filter(
            medio_pago=periodo.cuenta,
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
        
        # Construir filtro base
        filtros = Q(medio_pago=periodo.cuenta) | Q(cuenta_servicio=periodo.cuenta)
        
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

        filtros = Q(medio_pago=periodo.cuenta) | Q(cuenta_servicio=periodo.cuenta)
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
    model             = TipoCuenta
    template_name     = "tipocuenta/tipocuenta_form.html"
    fields            = ["codigo", "nombre"]
    success_url       = reverse_lazy("core:tipocuenta_list")
    success_message   = "Tipo de cuenta creado."
    

class TipoCuentaUpdateView(UpdateView):
    model = TipoCuenta
    fields = ['codigo', 'nombre', 'naturaleza']  # Ajusta los campos según tu modelo
    template_name = 'tipocuenta/tipocuenta_form.html'  # Ajusta la plantilla
    success_url = reverse_lazy('core:tipocuenta_list')  # URL de redirección


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
            "naturaleza": c.tipo.naturaleza  # Incluir naturaleza
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
            "naturaleza": c.tipo.naturaleza  # Incluir naturaleza
        } for c in cuentas
    ]
    return JsonResponse(data, safe=False)


class PeriodoPDFView(LoginRequiredMixin, View):
    def get(self, request, pk):
        periodo = get_object_or_404(Periodo, pk=pk)
        movs = Transaccion.objects.filter(
            medio_pago=periodo.cuenta,
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
    movimientos = Transaccion.objects.filter(
        Q(medio_pago=cuenta) | Q(cuenta_servicio=cuenta)
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
        'naturaleza': c.tipo.naturaleza,
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
        
        # Obtener movimientos paginados
        movimientos = cuenta.transacciones_pago.all().order_by('-fecha')
        paginator = Paginator(movimientos, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Determinar si la cuenta es de cargo o abono según la naturaleza de su tipo
        if cuenta.tipo and cuenta.tipo.naturaleza:
            naturaleza = cuenta.tipo.naturaleza
            es_cuenta_cargo = naturaleza in ['A', 'G']  # Activo o Gastos
        else:
            # Valor por defecto si no hay tipo o naturaleza definida
            es_cuenta_cargo = True
        
        # Calcular saldo acumulado y determinar tipo de movimiento
        saldo_acumulado = saldo_inicial
        for movimiento in page_obj:
            # Determinar si es cargo o abono
            movimiento.es_cargo = (movimiento.monto < 0) if es_cuenta_cargo else (movimiento.monto > 0)
            
            # Calcular saldo parcial
            saldo_acumulado += movimiento.monto
            movimiento.saldo_parcial = saldo_acumulado
            movimiento.monto_abs = abs(movimiento.monto)
            movimiento.saldo_parcial_abs = abs(movimiento.saldo_parcial)
        
        context['movimientos'] = page_obj
        context['es_cuenta_cargo'] = es_cuenta_cargo
        return context

