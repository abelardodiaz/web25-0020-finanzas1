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
from .filters import TransaccionFilter

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
from django.http import JsonResponse
from uuid import uuid4

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


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"


class CuentasView(LoginRequiredMixin, TemplateView):
    template_name = "cuentas/index.html"


class CategoriasView(LoginRequiredMixin, TemplateView):
    template_name = "categorias/index.html"


class TransaccionesView(LoginRequiredMixin, TemplateView):
    template_name = "transacciones/index.html"


class ReportesView(LoginRequiredMixin, TemplateView):
    template_name = "reportes/index.html"

# ——— Cuentas ———

class CuentaListView(ListView):
    model = Cuenta
    template_name = 'cuentas/index.html'
    context_object_name = 'cuentas'
    paginate_by = 25

class CuentaCreateView(SuccessMessageMixin, CreateView):
    model = Cuenta
    form_class = CuentaForm
    template_name = 'cuentas/cuentas_form.html'
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

    def get_queryset(self):
        # 1) Obtener queryset base y aplicar filtros normales
        qs_base = super().get_queryset()
        self.filterset = self.filterset_class(self.request.GET, queryset=qs_base)

        if self.filterset.is_valid():
            qs_filtrado = self.filterset.qs
            # 2) Tomar todos los grupo_uuid presentes en el resultado filtrado
            grupos = qs_filtrado.values_list("grupo_uuid", flat=True)
            # 3) Devolver TODOS los movimientos de esos grupos (pares completos)
            qs_completo = Transaccion.objects.filter(grupo_uuid__in=grupos).order_by("-fecha")
            return qs_completo

        # Si el filtro no es válido, regresa base
        return qs_base

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
                Transaccion.objects.create(
                    monto=-monto,
                    tipo=TransaccionTipo.GASTO,
                    fecha=fecha,
                    descripcion=desc,
                    medio_pago=origen,
                    categoria=categoria,
                    grupo_uuid=grupo,
                )
                Transaccion.objects.create(
                    monto=monto,
                    tipo=TransaccionTipo.INGRESO,
                    fecha=fecha,
                    descripcion=desc,
                    medio_pago=destino,
                    categoria=categoria,
                    grupo_uuid=grupo,
                )
                messages.success(self.request, "Transferencia registrada correctamente.")
                return super().form_valid(form)  # redirects using success_url

            # 1) movimiento principal estándar
            self.object = form.save()

            # 2) ¿hay doble partida para servicio?
            cs  = self.object.cuenta_servicio
            mp  = self.object.medio_pago
            if (not self.object.ajuste) and cs and cs != mp:
                Transaccion.objects.create(
                    monto        = -self.object.monto,            # signo opuesto
                    tipo         = (TransaccionTipo.INGRESO
                                        if self.object.tipo == TransaccionTipo.GASTO
                                        else TransaccionTipo.GASTO),
                    fecha        = self.object.fecha,
                    descripcion  = f"Pago {self.object.descripcion}",
                    cuenta_servicio = cs,                         # abono al servicio
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
                if pares_qs.exists():
                    par = pares_qs.first()
                    par.monto = -self.object.monto
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
                        monto = -self.object.monto,
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

        # Categoría especial "Transferencia" (crea si no existe)
        categoria, _ = Categoria.objects.get_or_create(nombre="Transferencia interna", defaults={"tipo": "INTERNA"})

        with transaction.atomic():
            # 1. Movimiento negativo en origen
            t1 = Transaccion.objects.create(
                monto        = -monto,
                fecha        = fecha,
                descripcion  = desc,
                medio_pago   = origen,
                categoria    = categoria,
                
            )
            # 2. Movimiento positivo en destino
            t2 = Transaccion.objects.create(
                monto        =  monto,
                fecha        =  fecha,
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
                .order_by("-fecha", "-id")           # fecha descendente
            )

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


class PeriodoCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
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


class PeriodoListView(LoginRequiredMixin, ListView):
    model = Periodo
    template_name = "periodos/index.html"
    context_object_name = "periodos"
    paginate_by = 50

    def get_queryset(self):
        return super().get_queryset().filter(generado=True)


# ----------------------------------------------------------------------
# Detalle de periodo (estado de cuenta)
# ----------------------------------------------------------------------


class PeriodoDetailView(LoginRequiredMixin, DetailView):
    model = Periodo
    template_name = "periodos/detalle.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        periodo = self.object
        movs = periodo.transacciones.order_by("fecha")
        ctx["movs"] = movs
        ctx["total_cargos"] = periodo.total_cargos
        ctx["total_abonos"] = periodo.total_abonos
        ctx["saldo"] = periodo.saldo
        return ctx

# ------------------------------------------------------------------
# Edición y eliminación de periodos
# ------------------------------------------------------------------


class PeriodoUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
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


class PeriodoDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """Confirma y elimina un periodo; las transacciones quedan sin periodo."""
    model = Periodo
    template_name = "periodos/confirm_delete.html"
    success_url = reverse_lazy("core:periodos_list")
    success_message = "Periodo eliminado correctamente."

# Actualizar movimientos manualmente (solo si abierto)
class PeriodoRefreshView(LoginRequiredMixin, View):
    def post(self, request, pk):
        periodo = get_object_or_404(Periodo, pk=pk)
        if periodo.cerrado:
            messages.warning(request, "El período está cerrado y no puede actualizarse.")
            return redirect('core:periodo_detail', pk=pk)

        # Reutilizar lógica de vinculación
        inicio = periodo.fecha_corte
        fin = periodo.fecha_fin_periodo or (periodo.fecha_corte + timedelta(days=30))

        filtros = Q(medio_pago=periodo.cuenta) | Q(cuenta_servicio=periodo.cuenta)
        if inicio and fin:
            filtros &= Q(fecha__range=(inicio, fin))

        Transaccion.objects.filter(periodo=periodo).exclude(filtros).update(periodo=None)
        Transaccion.objects.filter(filtros, periodo__isnull=True).update(periodo=periodo)

        # Registrar en historial (opcional)
        PeriodoEstadoLog.objects.create(
            periodo=periodo,
            accion="ACTUALIZAR",
            usuario=request.user,
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


class TipoCuentaListView(LoginRequiredMixin, ListView):
    model               = TipoCuenta
    template_name       = "tipocuenta/index.html"
    context_object_name = "tipos"
    ordering            = ["nombre"]

class TipoCuentaCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model             = TipoCuenta
    template_name     = "tipocuenta/tipocuenta_form.html"
    fields            = ["codigo", "nombre"]
    success_url       = reverse_lazy("core:tipocuenta_list")
    success_message   = "Tipo de cuenta creado."
    

# --- AJAX Endpoints -------------------------------------------------

def cuentas_servicio_json(request):
    """Devuelve cuentas cuyo tipo es 'SERV' (servicios)"""
    cuentas = Cuenta.objects.filter(tipo__codigo="SERV").order_by("nombre")
    data = [{"id": c.id, "text": str(c)} for c in cuentas]
    return JsonResponse(data, safe=False)


def categorias_json(request):
    """Devuelve todas las categorías ordenadas por nombre"""
    categorias = Categoria.objects.order_by("nombre")
    data = [{"id": cat.id, "text": str(cat)} for cat in categorias]
    return JsonResponse(data, safe=False)


def medios_pago_json(request):
    """Devuelve cuentas de tipo DEB o CRE (medios de pago)"""
    cuentas = Cuenta.objects.filter(tipo__grupo__in=["DEB", "CRE"]).order_by("nombre")
    data = [{"id": c.id, "text": str(c)} for c in cuentas]
    return JsonResponse(data, safe=False)


class PeriodoPDFView(LoginRequiredMixin, View):
    def get(self, request, pk):
        periodo = get_object_or_404(Periodo, pk=pk)
        movs = periodo.transacciones.order_by("fecha")
        
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
    
