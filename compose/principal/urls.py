from django.urls import path
from .views import (
    DashboardView,
    ReportesHomeView,
    ReporteMovimientosAnimalesView,
    ReporteProtocolosView,
    ReporteMovimientosInsumosView,
    ReporteConsumosView,
)

app_name = "principal"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),

    path("reportes/", ReportesHomeView.as_view(), name="reportes_home"),

    path("reportes/movimientos-animales/", ReporteMovimientosAnimalesView.as_view(),
         name="reporte_mov_animales"),

    path("reportes/protocolos/", ReporteProtocolosView.as_view(),
         name="reporte_protocolos"),

    path("reportes/movimientos-insumos/", ReporteMovimientosInsumosView.as_view(),
         name="reporte_mov_insumos"),

    path("reportes/consumos/", ReporteConsumosView.as_view(),
         name="reporte_consumos"),
]

