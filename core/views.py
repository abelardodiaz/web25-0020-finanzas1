# <!-- file: core/views.py -->
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView
)
from .models import Cuenta, Categoria, TipoCuenta
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
from .forms import TransferenciaForm, Periodo, IngresoForm, forms
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
    template_name = 'cuentas/form.html'
    success_url = reverse_lazy('core:cuentas_list')
    success_message = "Cuenta «%(nombre)s» creada correctamente."

class CuentaUpdateView(SuccessMessageMixin, UpdateView):
    model = Cuenta
    form_class = CuentaForm
    template_name = 'cuentas/form.html'
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
    template_name = 'categorias/form.html'
    success_url = reverse_lazy('core:categorias_list')
    success_message = "Categoría «%(nombre)s» creada correctamente."

class CategoriaUpdateView(SuccessMessageMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'categorias/form.html'
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

class TransaccionCreateView(SuccessMessageMixin, CreateView):
    model         = Transaccion
    form_class    = TransaccionForm
    template_name = "transacciones/tr_nueva.html"
    success_url   = reverse_lazy("core:transacciones_list")
    success_message = "Transacción registrada exitosamente."

    def form_valid(self, form):
        with transaction.atomic():
            self.object = form.save()              # 1) movimiento principal

            # 2) ¿hay doble partida?
            cs  = self.object.cuenta_servicio
            mp  = self.object.medio_pago
            if cs and cs != mp:
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
                )
        messages.success(self.request, self.success_message)
        return super().form_valid(form)

class TransferenciaCreateView(FormView):
    template_name  = "transferencias/form.html"
    form_class     = TransferenciaForm
    success_url    = reverse_lazy("core:transacciones_list")

    def form_valid(self, form):
        origen   = form.cleaned_data["cuenta_origen"]
        destino  = form.cleaned_data["cuenta_destino"]
        monto    = form.cleaned_data["monto"]
        fecha    = form.cleaned_data["fecha"]
        desc     = form.cleaned_data["descripcion"] or f"Transferencia {origen} → {destino}"

        # Categoría especial “Transferencia” (crea si no existe)
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
    template_name = "periodos/per_nuevo.html"
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
    

class PeriodoListView(LoginRequiredMixin, ListView):
    model = Periodo  # Cambiar a nuestro nuevo modelo único
    template_name = "periodos/index.html"
    context_object_name = "periodos"
    paginate_by = 50


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
    template_name     = "tipocuenta/form.html"
    fields            = ["codigo", "nombre"]
    success_url       = reverse_lazy("core:tipocuenta_list")
    success_message   = "Tipo de cuenta creado."
    
