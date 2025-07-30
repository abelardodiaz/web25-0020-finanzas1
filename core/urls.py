# <!-- file: core/urls.py -->
from django.urls import path, include
from .views import (
    CuentaListView, CuentaCreateView, CuentaUpdateView, CuentaDeleteView,
    CategoriaListView, CategoriaCreateView, CategoriaUpdateView, CategoriaDeleteView,
    DashboardView, TransaccionListView, TransaccionCreateView, ReportesView, 
    TransferenciaCreateView, EstadoCuentaView, PeriodoCreateView, PeriodoListView, PeriodoDetailView,
    PeriodoUpdateView, PeriodoDeleteView, TransaccionDeleteView, PeriodoRefreshView,
    IngresoCreateView, TipoCuentaCreateView, TipoCuentaListView, PeriodoPDFView
)
import core.views as core_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import View

app_name = "core"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),

    # Cuentas
    path("cuentas/", CuentaListView.as_view(), name="cuentas_list"),
    path("cuentas/nuevo/", CuentaCreateView.as_view(), name="cuentas_create"),
    path("cuentas/<int:pk>/editar/", CuentaUpdateView.as_view(), name="cuentas_edit"),
    path("cuentas/<int:pk>/eliminar/", CuentaDeleteView.as_view(), name="cuentas_delete"),

    # Categorías
    path("categorias/", CategoriaListView.as_view(), name="categorias_list"),
    path("categorias/nueva/", CategoriaCreateView.as_view(), name="categorias_create"),
    path("categorias/<int:pk>/editar/", CategoriaUpdateView.as_view(), name="categorias_edit"),
    path("categorias/<int:pk>/eliminar/", CategoriaDeleteView.as_view(), name="categorias_delete"),

    # Transacciones & Reportes (stubs)
    
    path("transacciones/", TransaccionListView.as_view(),
         name="transacciones_list"),
    path("transacciones/nueva/", TransaccionCreateView.as_view(),
         name="transacciones_create"),
    path("transacciones/<int:pk>/editar/", core_views.TransaccionUpdateView.as_view(),
         name="transacciones_edit"),
    path("transacciones/<int:pk>/eliminar/", core_views.TransaccionDeleteView.as_view(),
         name="transacciones_delete"),
    path("transacciones/refresh_cuentas/", core_views.cuentas_servicio_json, name="refresh_cuentas"),
    path("transacciones/refresh_categorias/", core_views.categorias_json, name="refresh_categorias"),
    path("transacciones/refresh_medios_pago/", core_views.medios_pago_json, name="refresh_medios_pago"),
    path("transacciones/refresh_medios/", core_views.medios_pago_json, name="refresh_medios"),


    path("transferencias/nueva/", TransferenciaCreateView.as_view(),
            name="transferencias_create"),

    path("reportes/estado-cuenta/", EstadoCuentaView.as_view(), name="reportes_estado_cuenta"),

    # Crear periodo CON cuenta específica
    path("cuentas/<int:cuenta_pk>/periodos/nuevo/",
         PeriodoCreateView.as_view(),
         name="periodos_create_for_account"),
    
    # Crear periodo SIN cuenta específica
    path("periodos/nuevo/",
         PeriodoCreateView.as_view(),
         name="periodos_create"),  

    
    path("periodos/", PeriodoListView.as_view(), name="periodos_list"),
    path("periodos/<int:pk>/", PeriodoDetailView.as_view(), name="periodo_detail"),
    path("periodos/<int:pk>/refresh/", core_views.PeriodoRefreshView.as_view(), name="periodo_refresh"),
    path("periodos/<int:pk>/cerrar/", core_views.CerrarPeriodoView.as_view(), name="periodo_cerrar"),
    path("periodos/<int:pk>/abrir/", core_views.AbrirPeriodoView.as_view(), name="periodo_abrir"),
    path("periodos/<int:pk>/editar/", PeriodoUpdateView.as_view(), name="periodo_edit"),
    path("periodos/<int:pk>/eliminar/", PeriodoDeleteView.as_view(), name="periodo_delete"),
    path("tipos-cuenta/", TipoCuentaListView.as_view(),  name="tipocuenta_list"), 
    path("tipos-cuenta/nuevo/", TipoCuentaCreateView.as_view(), name="tipocuenta_create"), 
    path("ingresos/nuevo/", IngresoCreateView.as_view(), name="ingreso_create"),  
    path('periodos/<int:pk>/pdf/', PeriodoPDFView.as_view(), name='periodo_pdf'),

]