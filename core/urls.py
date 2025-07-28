# <!-- file: core/urls.py -->
from django.urls import path, include
from .views import (
    CuentaListView, CuentaCreateView, CuentaUpdateView, CuentaDeleteView,
    CategoriaListView, CategoriaCreateView, CategoriaUpdateView, CategoriaDeleteView,
    DashboardView, TransaccionListView, TransaccionCreateView, ReportesView, 
    TransferenciaCreateView, EstadoCuentaView, PeriodoCreateView, PeriodoListView, IngresoCreateView,
    TipoCuentaCreateView, TipoCuentaListView
)

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
    path("tipos-cuenta/", TipoCuentaListView.as_view(),  name="tipocuenta_list"), 
    path("tipos-cuenta/nuevo/", TipoCuentaCreateView.as_view(), name="tipocuenta_create"), 
    path("ingresos/nuevo/", IngresoCreateView.as_view(), name="ingreso_create"),  

]