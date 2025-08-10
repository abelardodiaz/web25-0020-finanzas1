# <!-- file: core/urls.py -->
from django.urls import path, include
from .views import (
    CuentaListView, CuentaCreateView, CuentaUpdateView, CuentaDeleteView,
    CategoriaListView, CategoriaCreateView, CategoriaUpdateView, CategoriaDeleteView,
    DashboardView, TransaccionListView, TransaccionCreateView, ReportesView, 
    TransferenciaCreateView, EstadoCuentaView, PeriodoCreateView, PeriodoListView, PeriodoDetailView,
    PeriodoUpdateView, PeriodoDeleteView, TransaccionDeleteView, PeriodoRefreshView,
    IngresoCreateView, TipoCuentaCreateView, TipoCuentaListView, PeriodoPDFView, CuentaSaldosView, cuentas_autocomplete, cuenta_movimientos,
    UserProfileView, CuentaDetailView, TipoCuentaUpdateView, TipoCuentaDeleteView,
    # Nuevas vistas de conciliación
    cambiar_estado_transaccion, conciliacion_view, conciliar_masivo, TransaccionEstadoUpdateView,
    # Vistas de matching automático
    importacion_bancaria_view, importacion_detalle_view, aplicar_match_manual, 
    revertir_match, buscar_transacciones_candidatas, ejecutar_matching_masivo,
    # Vistas BBVA
    BBVASimpleView, BBVADetalleView, bbva_validar_movimiento, bbva_resumen_importacion,
    BBVAWizardView, BBVAWizardDetalladoView, BBVAResumenFinalView
)
# Vistas BBVA están ahora en views.py
import core.views as core_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import View
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.db.models import Sum
from .models import Cuenta, Transaccion
from django.shortcuts import render
from django.views.generic import TemplateView

app_name = "core"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),

    # Cuentas
    path("cuentas/", CuentaListView.as_view(), name="cuentas_list"),
    path("cuentas/nuevo/", CuentaCreateView.as_view(), name="cuentas_create"),
    path("cuentas/<int:pk>/editar/", CuentaUpdateView.as_view(), name="cuentas_edit"),
    path("cuentas/<int:pk>/eliminar/", CuentaDeleteView.as_view(), name="cuentas_delete"),
    path('cuentas/saldos/', CuentaSaldosView.as_view(), name='cuentas_saldos'),
    path('cuentas/autocomplete/', cuentas_autocomplete, name='cuentas_autocomplete'),
    path('cuenta/movimientos/', cuenta_movimientos, name='cuenta_movimientos'),
    path('cuentas/detalle/<int:pk>/', CuentaDetailView.as_view(), name='cuenta_detail'),

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
    path('periodos/<int:pk>/corregir-saldo/', core_views.CorregirSaldoInicialView.as_view(), name='periodo_corregir_saldo'),
    path('perfil/', core_views.UserProfileView.as_view(), name='user_profile'),
    path('cuentas/', CuentaListView.as_view(), name='cuenta_list'),
    path('cuentas/nueva/', CuentaCreateView.as_view(), name='cuenta_create'),
    path('cuentas/editar/<int:pk>/', CuentaUpdateView.as_view(), name='cuenta_edit'),
    path('cuentas/eliminar/<int:pk>/', CuentaDeleteView.as_view(), name='cuenta_delete'),
    path('periodos/detalle/<int:pk>/', PeriodoDetailView.as_view(), name='periodo_detail'),
    path('tipo-cuenta/<int:pk>/', TipoCuentaUpdateView.as_view(), name='tipocuenta_update'),
    path('tipo-cuenta/eliminar/<int:pk>/', TipoCuentaDeleteView.as_view(), name='tipocuenta_delete'),
    
    # URLs de conciliación bancaria
    path('conciliacion/', conciliacion_view, name='conciliacion'),
    path('transaccion/<int:transaccion_id>/estado/', cambiar_estado_transaccion, name='cambiar_estado_transaccion'),
    path('conciliacion/masivo/', conciliar_masivo, name='conciliar_masivo'),
    path('transaccion/<int:pk>/actualizar-estado/', TransaccionEstadoUpdateView.as_view(), name='transaccion_estado_update'),
    
    # URLs de matching automático e importación
    path('importacion/', importacion_bancaria_view, name='importacion_bancaria'),
    path('importacion/<int:importacion_id>/', importacion_detalle_view, name='importacion_detalle'),
    path('importacion/<int:importacion_id>/matching-masivo/', ejecutar_matching_masivo, name='matching_masivo'),
    path('api/match/manual/', aplicar_match_manual, name='aplicar_match_manual'),
    path('api/match/revertir/', revertir_match, name='revertir_match'),
    path('api/transacciones/candidatas/', buscar_transacciones_candidatas, name='buscar_candidatas'),
    
    # URLs de importación BBVA
    path('bbva/', BBVASimpleView.as_view(), name='bbva_simple'),
    path('bbva/wizard/', BBVAWizardView.as_view(), name='bbva_wizard'),
    path('bbva/wizard-detallado/<int:importacion_id>/', BBVAWizardDetalladoView.as_view(), name='bbva_wizard_detallado'),
    path('bbva/resumen-final/<int:importacion_id>/', BBVAResumenFinalView.as_view(), name='bbva_resumen_final'),
    path('bbva/<int:importacion_id>/', BBVADetalleView.as_view(), name='bbva_detalle'),
    path('bbva/validar/<int:movimiento_id>/', bbva_validar_movimiento, name='bbva_validar_movimiento'),
    path('bbva/resumen/<int:importacion_id>/', bbva_resumen_importacion, name='bbva_resumen_importacion'),
]